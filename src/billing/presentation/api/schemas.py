from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from billing.domain.value_objects import BillingPeriod, Currency, InvoiceStatus, SubscriptionStatus


class CreateTenantRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    currency: Currency = Currency.RUB


class TenantResponse(BaseModel):
    id: str
    name: str
    currency: Currency
    created_at: datetime
    is_active: bool


class CreatePlanRequest(BaseModel):
    tenant_id: str
    name: str = Field(..., min_length=2, max_length=100)
    price: Decimal = Field(..., ge=0)
    currency: Currency = Currency.RUB
    period: BillingPeriod = BillingPeriod.MONTHLY
    included_units: int = Field(0, ge=0)
    overage_unit_price: Decimal = Field(Decimal("0.00"), ge=0)
    trial_days: int = Field(0, ge=0)


class PlanResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    price: Decimal
    currency: Currency
    period: BillingPeriod
    included_units: int
    overage_unit_price: Decimal
    trial_days: int
    is_active: bool
    version: int


class SubscribeRequest(BaseModel):
    tenant_id: str
    customer_id: str
    plan_id: str
    payment_method_id: str
    idempotency_key: str = Field(..., min_length=1)


class LineItemResponse(BaseModel):
    description: str
    amount: Decimal
    currency: Currency
    quantity: int
    total: Decimal


class InvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    subscription_id: Optional[str]
    status: InvoiceStatus
    currency: Currency
    total_amount: Decimal
    line_items: List[LineItemResponse]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    failure_reason: Optional[str]


class SubscriptionResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime]
    cancel_at_period_end: bool
    retry_count: int


class SubscribeResponse(BaseModel):
    subscription: SubscriptionResponse
    invoice: InvoiceResponse


class ChangePlanRequest(BaseModel):
    tenant_id: str
    new_plan_id: str
    payment_method_id: str
    idempotency_key: str = Field(..., min_length=1)


class ProrationDetailsResponse(BaseModel):
    unspent_credit: Decimal
    new_plan_charge: Decimal
    net_amount_due: Decimal
    remaining_days: int
    total_period_days: int


class ChangePlanResponse(BaseModel):
    subscription: SubscriptionResponse
    invoice: InvoiceResponse
    proration: ProrationDetailsResponse


class RecordUsageRequest(BaseModel):
    tenant_id: str
    subscription_id: str
    metric_name: str
    units: int = Field(..., gt=0)


class RecordUsageResponse(BaseModel):
    id: str
    tenant_id: str
    subscription_id: str
    units: int
    recorded_at: datetime


class BillingCycleResponse(BaseModel):
    renewed_count: int
    failed_count: int
    renewed_subscriptions: List[str]
    failed_subscriptions: List[str]
    invoices_generated: List[str]
