from dataclasses import dataclass
from datetime import timedelta
import uuid

from billing.application.ports.clock import IClock
from billing.application.ports.payment_gateway import IPaymentGateway
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
    ITenantRepository,
)
from billing.domain.entities import Invoice, Subscription
from billing.domain.exceptions import (
    PlanInactiveError,
    TenantMismatchError,
)
from billing.domain.value_objects import SubscriptionStatus


@dataclass(frozen=True)
class SubscribeCustomerCommand:
    tenant_id: str
    customer_id: str
    plan_id: str
    payment_method_id: str
    idempotency_key: str


@dataclass(frozen=True)
class SubscribeCustomerResult:
    subscription: Subscription
    invoice: Invoice


class SubscribeCustomerUseCase:
    """Orchestrates subscribing a customer to a plan with trial or initial charge."""

    def __init__(
        self,
        tenant_repo: ITenantRepository,
        plan_repo: IPlanRepository,
        subscription_repo: ISubscriptionRepository,
        invoice_repo: IInvoiceRepository,
        payment_gateway: IPaymentGateway,
        clock: IClock,
    ) -> None:
        self.tenant_repo = tenant_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.invoice_repo = invoice_repo
        self.payment_gateway = payment_gateway
        self.clock = clock

    def execute(self, cmd: SubscribeCustomerCommand) -> SubscribeCustomerResult:
        # 1. Idempotency check on invoice
        existing_invoice = self.invoice_repo.get_by_idempotency_key(cmd.tenant_id, cmd.idempotency_key)
        if existing_invoice and existing_invoice.subscription_id:
            sub = self.subscription_repo.get_by_id(existing_invoice.subscription_id)
            if sub:
                return SubscribeCustomerResult(subscription=sub, invoice=existing_invoice)

        # 2. Validate tenant and plan
        tenant = self.tenant_repo.get_by_id(cmd.tenant_id)
        if not tenant or not tenant.is_active:
            raise TenantMismatchError(f"Tenant {cmd.tenant_id} does not exist or is inactive")

        plan = self.plan_repo.get_by_id(cmd.plan_id)
        if not plan or not plan.is_active:
            raise PlanInactiveError(f"Plan {cmd.plan_id} is not found or inactive")
        if plan.tenant_id != cmd.tenant_id:
            raise TenantMismatchError("Plan belongs to another tenant")

        now = self.clock.now()
        sub_id = str(uuid.uuid4())
        period_days = plan.period.approx_days

        # 3. Handle trial vs immediate activation
        if plan.trial_days > 0:
            trial_end = now + timedelta(days=plan.trial_days)
            subscription = Subscription(
                id=sub_id,
                tenant_id=cmd.tenant_id,
                customer_id=cmd.customer_id,
                plan_id=plan.id,
                status=SubscriptionStatus.TRIALING,
                current_period_start=now,
                current_period_end=trial_end,
                trial_end=trial_end,
            )
            # Dummy $0 invoice for trial confirmation
            invoice = Invoice(
                id=str(uuid.uuid4()),
                tenant_id=cmd.tenant_id,
                customer_id=cmd.customer_id,
                subscription_id=sub_id,
                currency=plan.price.currency,
                idempotency_key=cmd.idempotency_key,
            )
            invoice.add_item(description=f"Free Trial: {plan.name}", amount=plan.price.zero(plan.price.currency))
            invoice.issue(due_date=now)
            invoice.mark_paid(paid_at=now)

            self.subscription_repo.save(subscription)
            self.invoice_repo.save(invoice)
            return SubscribeCustomerResult(subscription=subscription, invoice=invoice)

        # Immediate billing
        period_end = now + timedelta(days=period_days)
        subscription = Subscription(
            id=sub_id,
            tenant_id=cmd.tenant_id,
            customer_id=cmd.customer_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=period_end,
        )

        invoice = Invoice(
            id=str(uuid.uuid4()),
            tenant_id=cmd.tenant_id,
            customer_id=cmd.customer_id,
            subscription_id=sub_id,
            currency=plan.price.currency,
            idempotency_key=cmd.idempotency_key,
        )
        invoice.add_item(description=f"Initial Subscription: {plan.name}", amount=plan.price)
        invoice.issue(due_date=now)

        # Attempt gateway charge
        charge_result = self.payment_gateway.charge(
            invoice=invoice,
            payment_method_id=cmd.payment_method_id,
            idempotency_key=cmd.idempotency_key,
        )

        if charge_result.success:
            invoice.mark_paid(paid_at=now)
            subscription.status = SubscriptionStatus.ACTIVE
        else:
            invoice.mark_failed(reason=charge_result.error_message or "Payment rejected")
            subscription.mark_past_due()

        self.subscription_repo.save(subscription)
        self.invoice_repo.save(invoice)

        return SubscribeCustomerResult(subscription=subscription, invoice=invoice)
