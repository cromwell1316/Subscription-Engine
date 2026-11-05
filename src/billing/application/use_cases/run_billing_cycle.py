from dataclasses import dataclass
from datetime import timedelta
from typing import List
import uuid

from billing.application.ports.clock import IClock
from billing.application.ports.payment_gateway import IPaymentGateway
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
    IUsageRepository,
)
from billing.domain.entities import Invoice, Subscription
from billing.domain.value_objects import SubscriptionStatus


@dataclass(frozen=True)
class BillingCycleResult:
    renewed_subscriptions: List[str]
    failed_subscriptions: List[str]
    invoices_generated: List[str]


class RunBillingCycleUseCase:
    """Processes recurring billing renewals, metered overages, and smart retries."""

    MAX_RETRY_ATTEMPTS = 3

    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        plan_repo: IPlanRepository,
        invoice_repo: IInvoiceRepository,
        usage_repo: IUsageRepository,
        payment_gateway: IPaymentGateway,
        clock: IClock,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.usage_repo = usage_repo
        self.payment_gateway = payment_gateway
        self.clock = clock

    def execute(self) -> BillingCycleResult:
        now = self.clock.now()
        due_subs = self.subscription_repo.list_due_for_renewal(as_of=now)

        renewed: List[str] = []
        failed: List[str] = []
        invoices: List[str] = []

        for sub in due_subs:
            plan = self.plan_repo.get_by_id(sub.plan_id)
            if not plan or not plan.is_active:
                continue

            # Check if cancellation at period end was requested
            if sub.cancel_at_period_end:
                sub.cancel(immediate=True)
                self.subscription_repo.save(sub)
                continue

            # Calculate metered usage overages for the ending period
            total_usage = self.usage_repo.get_total_units(
                tenant_id=sub.tenant_id,
                subscription_id=sub.id,
                start_time=sub.current_period_start,
                end_time=sub.current_period_end,
            )

            overage_units = max(0, total_usage - plan.included_units)
            overage_cost = (
                plan.overage_unit_price * overage_units
                if plan.overage_unit_price
                else plan.price.zero(plan.price.currency)
            )

            # Generate renewal invoice
            cycle_key = f"renewal-{sub.id}-{int(now.timestamp())}"
            invoice = Invoice(
                id=str(uuid.uuid4()),
                tenant_id=sub.tenant_id,
                customer_id=sub.customer_id,
                subscription_id=sub.id,
                currency=plan.price.currency,
                idempotency_key=cycle_key,
            )
            invoice.add_item(description=f"Renewal: {plan.name}", amount=plan.price)
            if overage_cost.is_positive():
                invoice.add_item(
                    description=f"Metered overage ({overage_units} units)",
                    amount=overage_cost,
                )
            invoice.issue(due_date=now)

            # Process payment
            charge_result = self.payment_gateway.charge(
                invoice=invoice,
                payment_method_id="default-card",
                idempotency_key=cycle_key,
            )

            if charge_result.success:
                invoice.mark_paid(paid_at=now)
                new_start = sub.current_period_end
                new_end = new_start + timedelta(days=plan.period.approx_days)
                sub.activate(period_start=new_start, period_end=new_end)
                renewed.append(sub.id)
            else:
                invoice.mark_failed(reason=charge_result.error_message or "Renewal payment declined")
                sub.mark_past_due()
                if sub.retry_count >= self.MAX_RETRY_ATTEMPTS:
                    sub.pause()
                failed.append(sub.id)

            self.invoice_repo.save(invoice)
            self.subscription_repo.save(sub)
            invoices.append(invoice.id)

        return BillingCycleResult(
            renewed_subscriptions=renewed,
            failed_subscriptions=failed,
            invoices_generated=invoices,
        )
