from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TenantModel(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default="RUB")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)

    plans = relationship("PlanModel", back_populates="tenant", cascade="all, delete-orphan")


class PlanModel(Base):
    __tablename__ = "plans"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    price_amount = Column(Numeric(12, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)
    period = Column(String(20), nullable=False, default="MONTHLY")
    included_units = Column(Integer, nullable=False, default=0)
    overage_unit_price = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    trial_days = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    version = Column(Integer, nullable=False, default=1)

    tenant = relationship("TenantModel", back_populates="plans")


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    plan_id = Column(String(64), ForeignKey("plans.id"), nullable=False)
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False, index=True)
    trial_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)
    retry_count = Column(Integer, nullable=False, default=0)


class InvoiceModel(Base):
    __tablename__ = "invoices"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    subscription_id = Column(String(64), ForeignKey("subscriptions.id"), nullable=True, index=True)
    status = Column(String(30), nullable=False, default="DRAFT", index=True)
    currency = Column(String(3), nullable=False)
    idempotency_key = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    line_items = relationship("InvoiceLineItemModel", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLineItemModel(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String(64), ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    invoice = relationship("InvoiceModel", back_populates="line_items")


class UsageRecordModel(Base):
    __tablename__ = "usage_records"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    subscription_id = Column(String(64), ForeignKey("subscriptions.id"), nullable=False, index=True)
    units = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True, index=True)
