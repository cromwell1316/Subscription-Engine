from dataclasses import dataclass
import uuid

from billing.application.ports.clock import IClock
from billing.application.ports.payment_gateway import IPaymentGateway
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
)
from billing.domain.entities import Invoice, Subscription
from billing.domain.exceptions import (
    PlanInactiveError,
    SubscriptionNotActiveError,
    TenantMismatchError,
)
from billing.domain.value_objects import ProrationResult, SubscriptionStatus


@dataclass(frozen=True)
class ChangePlanCommand:
    tenant_id: str
    subscription_id: str
    new_plan_id: str
    payment_method_id: str
    idempotency_key: str


@dataclass(frozen=True)
class ChangePlanResult:
    subscription: Subscription
    invoice: Invoice
    proration: ProrationResult


class ChangePlanUseCase:
    """Orchestrates changing a customer's subscription plan with prorated calculation."""

    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        plan_repo: IPlanRepository,
        invoice_repo: IInvoiceRepository,
        payment_gateway: IPaymentGateway,
        clock: IClock,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.payment_gateway = payment_gateway
        self.clock = clock

    def execute(self, cmd: ChangePlanCommand) -> ChangePlanResult:
        sub = self.subscription_repo.get_by_id(cmd.subscription_id)
        if not sub or sub.tenant_id != cmd.tenant_id:
            raise TenantMismatchError(f"Subscription {cmd.subscription_id} not found for tenant")

        if sub.status != SubscriptionStatus.ACTIVE:
            raise SubscriptionNotActiveError(f"Cannot change plan on subscription in status {sub.status.value}")

        current_plan = self.plan_repo.get_by_id(sub.plan_id)
        new_plan = self.plan_repo.get_by_id(cmd.new_plan_id)

        if not current_plan or not new_plan or not new_plan.is_active:
            raise PlanInactiveError(f"Target plan {cmd.new_plan_id} is inactive or does not exist")

        now = self.clock.now()
        proration = sub.calculate_proration(current_plan=current_plan, new_plan=new_plan, at_time=now)

        invoice = Invoice(
            id=str(uuid.uuid4()),
            tenant_id=cmd.tenant_id,
            customer_id=sub.customer_id,
            subscription_id=sub.id,
            currency=new_plan.price.currency,
            idempotency_key=cmd.idempotency_key,
        )

        if proration.unspent_credit.is_positive():
            invoice.add_item(
                description=f"Unused credit: {current_plan.name} ({proration.remaining_days} days)",
                amount=proration.unspent_credit.zero(proration.unspent_credit.currency),  # credit offset
            )

        if proration.net_amount_due.is_positive():
            invoice.add_item(
                description=f"Prorated upgrade to {new_plan.name} ({proration.remaining_days} days remaining)",
                amount=proration.net_amount_due,
            )
            invoice.issue(due_date=now)

            charge_result = self.payment_gateway.charge(
                invoice=invoice,
                payment_method_id=cmd.payment_method_id,
                idempotency_key=cmd.idempotency_key,
            )

            if not charge_result.success:
                invoice.mark_failed(reason=charge_result.error_message or "Upgrade charge failed")
                self.invoice_repo.save(invoice)
                # Keep subscription on current plan if charge fails!
                return ChangePlanResult(subscription=sub, invoice=invoice, proration=proration)

            invoice.mark_paid(paid_at=now)
        else:
            # Upgrade is free or credit exceeds cost
            invoice.issue(due_date=now)
            invoice.mark_paid(paid_at=now)

        sub.apply_plan_change(new_plan.id)
        self.subscription_repo.save(sub)
        self.invoice_repo.save(invoice)

        return ChangePlanResult(subscription=sub, invoice=invoice, proration=proration)
