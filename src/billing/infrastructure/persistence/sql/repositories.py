from datetime import datetime, timezone
from decimal import Decimal
import json
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from billing.application.ports.outbox import IOutboxRepository
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
    ITenantRepository,
    IUsageRepository,
)
from billing.domain.entities import (
    Invoice,
    InvoiceLineItem,
    Plan,
    Subscription,
    Tenant,
    UsageRecord,
)
from billing.domain.events import DomainEvent
from billing.domain.value_objects import (
    BillingPeriod,
    Currency,
    InvoiceStatus,
    Money,
    SubscriptionStatus,
)
from billing.infrastructure.persistence.sql.models import (
    InvoiceLineItemModel,
    InvoiceModel,
    OutboxMessageModel,
    PlanModel,
    SubscriptionModel,
    TenantModel,
    UsageRecordModel,
)


class SqlAlchemyTenantRepository(ITenantRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, tenant: Tenant) -> None:
        model = self.session.query(TenantModel).filter_by(id=tenant.id).first()
        if not model:
            model = TenantModel(id=tenant.id)
            self.session.add(model)
        model.name = tenant.name
        model.currency = tenant.currency.value
        model.created_at = tenant.created_at
        model.is_active = tenant.is_active
        self.session.flush()

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        model = self.session.query(TenantModel).filter_by(id=tenant_id).first()
        if not model:
            return None
        return Tenant(
            id=model.id,
            name=model.name,
            currency=Currency(model.currency),
            created_at=model.created_at,
            is_active=model.is_active,
        )

    def list_all(self) -> List[Tenant]:
        models = self.session.query(TenantModel).all()
        return [
            Tenant(
                id=m.id,
                name=m.name,
                currency=Currency(m.currency),
                created_at=m.created_at,
                is_active=m.is_active,
            )
            for m in models
        ]


class SqlAlchemyPlanRepository(IPlanRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, plan: Plan) -> None:
        model = self.session.query(PlanModel).filter_by(id=plan.id).first()
        if not model:
            model = PlanModel(id=plan.id)
            self.session.add(model)
        model.tenant_id = plan.tenant_id
        model.name = plan.name
        model.price_amount = plan.price.amount
        model.price_currency = plan.price.currency.value
        model.period = plan.period.value
        model.included_units = plan.included_units
        model.overage_unit_price = plan.overage_unit_price.amount if plan.overage_unit_price else Decimal("0.00")
        model.trial_days = plan.trial_days
        model.is_active = plan.is_active
        model.version = plan.version
        self.session.flush()

    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        model = self.session.query(PlanModel).filter_by(id=plan_id).first()
        if not model:
            return None
        curr = Currency(model.price_currency)
        return Plan(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            price=Money(amount=Decimal(str(model.price_amount)), currency=curr),
            period=BillingPeriod(model.period),
            included_units=model.included_units,
            overage_unit_price=Money(amount=Decimal(str(model.overage_unit_price)), currency=curr),
            trial_days=model.trial_days,
            is_active=model.is_active,
            version=model.version,
        )

    def list_by_tenant(self, tenant_id: str) -> List[Plan]:
        models = self.session.query(PlanModel).filter_by(tenant_id=tenant_id).all()
        plans = []
        for m in models:
            curr = Currency(m.price_currency)
            plans.append(
                Plan(
                    id=m.id,
                    tenant_id=m.tenant_id,
                    name=m.name,
                    price=Money(amount=Decimal(str(m.price_amount)), currency=curr),
                    period=BillingPeriod(m.period),
                    included_units=m.included_units,
                    overage_unit_price=Money(amount=Decimal(str(m.overage_unit_price)), currency=curr),
                    trial_days=m.trial_days,
                    is_active=m.is_active,
                    version=m.version,
                )
            )
        return plans


class SqlAlchemySubscriptionRepository(ISubscriptionRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, subscription: Subscription) -> None:
        model = self.session.query(SubscriptionModel).filter_by(id=subscription.id).first()
        if not model:
            model = SubscriptionModel(id=subscription.id)
            self.session.add(model)
        model.tenant_id = subscription.tenant_id
        model.customer_id = subscription.customer_id
        model.plan_id = subscription.plan_id
        model.status = subscription.status.value
        model.current_period_start = subscription.current_period_start
        model.current_period_end = subscription.current_period_end
        model.trial_end = subscription.trial_end
        model.cancel_at_period_end = subscription.cancel_at_period_end
        model.retry_count = subscription.retry_count
        self.session.flush()

    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        model = self.session.query(SubscriptionModel).filter_by(id=subscription_id).first()
        if not model:
            return None
        return Subscription(
            id=model.id,
            tenant_id=model.tenant_id,
            customer_id=model.customer_id,
            plan_id=model.plan_id,
            status=SubscriptionStatus(model.status),
            current_period_start=model.current_period_start.replace(tzinfo=timezone.utc)
            if model.current_period_start.tzinfo is None
            else model.current_period_start,
            current_period_end=model.current_period_end.replace(tzinfo=timezone.utc)
            if model.current_period_end.tzinfo is None
            else model.current_period_end,
            trial_end=model.trial_end.replace(tzinfo=timezone.utc)
            if model.trial_end and model.trial_end.tzinfo is None
            else model.trial_end,
            cancel_at_period_end=model.cancel_at_period_end,
            retry_count=model.retry_count,
        )

    def list_by_customer(self, tenant_id: str, customer_id: str) -> List[Subscription]:
        models = (
            self.session.query(SubscriptionModel)
            .filter_by(tenant_id=tenant_id, customer_id=customer_id)
            .all()
        )
        return [
            Subscription(
                id=m.id,
                tenant_id=m.tenant_id,
                customer_id=m.customer_id,
                plan_id=m.plan_id,
                status=SubscriptionStatus(m.status),
                current_period_start=m.current_period_start.replace(tzinfo=timezone.utc)
                if m.current_period_start.tzinfo is None
                else m.current_period_start,
                current_period_end=m.current_period_end.replace(tzinfo=timezone.utc)
                if m.current_period_end.tzinfo is None
                else m.current_period_end,
                trial_end=m.trial_end.replace(tzinfo=timezone.utc)
                if m.trial_end and m.trial_end.tzinfo is None
                else m.trial_end,
                cancel_at_period_end=m.cancel_at_period_end,
                retry_count=m.retry_count,
            )
            for m in models
        ]

    def list_due_for_renewal(self, as_of: datetime) -> List[Subscription]:
        # Handle naive vs timezone comparison
        cmp_date = as_of.replace(tzinfo=None) if as_of.tzinfo else as_of
        models = (
            self.session.query(SubscriptionModel)
            .filter(SubscriptionModel.current_period_end <= cmp_date)
            .all()
        )
        return [
            Subscription(
                id=m.id,
                tenant_id=m.tenant_id,
                customer_id=m.customer_id,
                plan_id=m.plan_id,
                status=SubscriptionStatus(m.status),
                current_period_start=m.current_period_start.replace(tzinfo=timezone.utc)
                if m.current_period_start.tzinfo is None
                else m.current_period_start,
                current_period_end=m.current_period_end.replace(tzinfo=timezone.utc)
                if m.current_period_end.tzinfo is None
                else m.current_period_end,
                trial_end=m.trial_end.replace(tzinfo=timezone.utc)
                if m.trial_end and m.trial_end.tzinfo is None
                else m.trial_end,
                cancel_at_period_end=m.cancel_at_period_end,
                retry_count=m.retry_count,
            )
            for m in models
        ]


class SqlAlchemyInvoiceRepository(IInvoiceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, invoice: Invoice) -> None:
        model = self.session.query(InvoiceModel).filter_by(id=invoice.id).first()
        if not model:
            model = InvoiceModel(id=invoice.id)
            self.session.add(model)
        model.tenant_id = invoice.tenant_id
        model.customer_id = invoice.customer_id
        model.subscription_id = invoice.subscription_id
        model.status = invoice.status.value
        model.currency = invoice.currency.value
        model.idempotency_key = invoice.idempotency_key
        model.created_at = invoice.created_at
        model.due_date = invoice.due_date
        model.paid_at = invoice.paid_at
        model.failure_reason = invoice.failure_reason

        # Synchronize line items
        self.session.query(InvoiceLineItemModel).filter_by(invoice_id=invoice.id).delete()
        for item in invoice.line_items:
            item_model = InvoiceLineItemModel(
                invoice_id=invoice.id,
                description=item.description,
                amount=item.amount.amount,
                currency=item.amount.currency.value,
                quantity=item.quantity,
            )
            self.session.add(item_model)

        self.session.flush()

    def _to_entity(self, model: InvoiceModel) -> Invoice:
        curr = Currency(model.currency)
        items = []
        for line in model.line_items:
            items.append(
                InvoiceLineItem(
                    description=line.description,
                    amount=Money(amount=Decimal(str(line.amount)), currency=Currency(line.currency)),
                    quantity=line.quantity,
                )
            )
        return Invoice(
            id=model.id,
            tenant_id=model.tenant_id,
            customer_id=model.customer_id,
            subscription_id=model.subscription_id,
            currency=curr,
            status=InvoiceStatus(model.status),
            line_items=items,
            idempotency_key=model.idempotency_key,
            created_at=model.created_at.replace(tzinfo=timezone.utc)
            if model.created_at.tzinfo is None
            else model.created_at,
            due_date=model.due_date.replace(tzinfo=timezone.utc)
            if model.due_date and model.due_date.tzinfo is None
            else model.due_date,
            paid_at=model.paid_at.replace(tzinfo=timezone.utc)
            if model.paid_at and model.paid_at.tzinfo is None
            else model.paid_at,
            failure_reason=model.failure_reason,
        )

    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        model = self.session.query(InvoiceModel).filter_by(id=invoice_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[Invoice]:
        model = (
            self.session.query(InvoiceModel)
            .filter_by(tenant_id=tenant_id, idempotency_key=key)
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def list_by_subscription(self, subscription_id: str) -> List[Invoice]:
        models = self.session.query(InvoiceModel).filter_by(subscription_id=subscription_id).all()
        return [self._to_entity(m) for m in models]


class SqlAlchemyUsageRepository(IUsageRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, record: UsageRecord) -> None:
        model = UsageRecordModel(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            subscription_id=record.subscription_id,
            units=record.units,
            recorded_at=record.recorded_at,
        )
        self.session.add(model)
        self.session.flush()

    def get_total_units(
        self,
        tenant_id: str,
        subscription_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        start_cmp = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
        end_cmp = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time

        result = (
            self.session.query(func.coalesce(func.sum(UsageRecordModel.units), 0))
            .filter(
                UsageRecordModel.tenant_id == tenant_id,
                UsageRecordModel.subscription_id == subscription_id,
                UsageRecordModel.recorded_at >= start_cmp,
                UsageRecordModel.recorded_at <= end_cmp,
            )
            .scalar()
        )
        return int(result)


class SqlAlchemyOutboxRepository(IOutboxRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_event(self, event: DomainEvent) -> None:
        # Serialize event dataclass payload to JSON
        payload = {k: str(v) if isinstance(v, (Decimal, datetime)) else v for k, v in event.__dict__.items()}
        msg = OutboxMessageModel(
            id=event.event_id,
            tenant_id=event.tenant_id,
            event_type=event.event_type,
            payload_json=json.dumps(payload),
            occurred_at=event.occurred_at,
            published_at=None,
        )
        self.session.add(msg)
        self.session.flush()

    def list_unpublished(self, limit: int = 50) -> List[DomainEvent]:
        # Outbox querying
        messages = (
            self.session.query(OutboxMessageModel)
            .filter(OutboxMessageModel.published_at.is_(None))
            .order_by(OutboxMessageModel.occurred_at.asc())
            .limit(limit)
            .all()
        )
        events = []
        for m in messages:
            events.append(
                DomainEvent(
                    event_id=m.id,
                    occurred_at=m.occurred_at,
                    tenant_id=m.tenant_id,
                )
            )
        return events

    def mark_published(self, event_id: str) -> None:
        msg = self.session.query(OutboxMessageModel).filter_by(id=event_id).first()
        if msg:
            msg.published_at = datetime.now(timezone.utc)
            self.session.flush()
