from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from billing.application.use_cases.change_plan import ChangePlanCommand
from billing.application.use_cases.subscribe_customer import SubscribeCustomerCommand
from billing.domain.entities import Invoice, Subscription
from billing.domain.exceptions import (
    BillingDomainError,
    PlanInactiveError,
    SubscriptionNotActiveError,
    TenantMismatchError,
)
from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.schemas import (
    ChangePlanRequest,
    ChangePlanResponse,
    InvoiceResponse,
    LineItemResponse,
    ProrationDetailsResponse,
    SubscribeRequest,
    SubscribeResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def _serialize_subscription(sub: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=sub.id,
        tenant_id=sub.tenant_id,
        customer_id=sub.customer_id,
        plan_id=sub.plan_id,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        trial_end=sub.trial_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        retry_count=sub.retry_count,
    )


def _serialize_invoice(inv: Invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        customer_id=inv.customer_id,
        subscription_id=inv.subscription_id,
        status=inv.status,
        currency=inv.currency,
        total_amount=inv.total_amount.amount,
        line_items=[
            LineItemResponse(
                description=item.description,
                amount=item.amount.amount,
                currency=item.amount.currency,
                quantity=item.quantity,
                total=item.total.amount,
            )
            for item in inv.line_items
        ],
        due_date=inv.due_date,
        paid_at=inv.paid_at,
        failure_reason=inv.failure_reason,
    )


@router.post("", response_model=SubscribeResponse, status_code=status.HTTP_201_CREATED)
def subscribe_customer(
    req: SubscribeRequest,
    container: ServiceContainer = Depends(get_container),
) -> SubscribeResponse:
    use_case = container.get_subscribe_use_case()
    cmd = SubscribeCustomerCommand(
        tenant_id=req.tenant_id,
        customer_id=req.customer_id,
        plan_id=req.plan_id,
        payment_method_id=req.payment_method_id,
        idempotency_key=req.idempotency_key,
    )
    try:
        result = use_case.execute(cmd)
    except (TenantMismatchError, PlanInactiveError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BillingDomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return SubscribeResponse(
        subscription=_serialize_subscription(result.subscription),
        invoice=_serialize_invoice(result.invoice),
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: str,
    container: ServiceContainer = Depends(get_container),
) -> SubscriptionResponse:
    sub = container.subscription_repo.get_by_id(subscription_id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription {subscription_id} not found",
        )
    return _serialize_subscription(sub)


@router.post("/{subscription_id}/change-plan", response_model=ChangePlanResponse)
def change_plan(
    subscription_id: str,
    req: ChangePlanRequest,
    container: ServiceContainer = Depends(get_container),
) -> ChangePlanResponse:
    use_case = container.get_change_plan_use_case()
    cmd = ChangePlanCommand(
        tenant_id=req.tenant_id,
        subscription_id=subscription_id,
        new_plan_id=req.new_plan_id,
        payment_method_id=req.payment_method_id,
        idempotency_key=req.idempotency_key,
    )
    try:
        result = use_case.execute(cmd)
    except (TenantMismatchError, PlanInactiveError, SubscriptionNotActiveError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BillingDomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return ChangePlanResponse(
        subscription=_serialize_subscription(result.subscription),
        invoice=_serialize_invoice(result.invoice),
        proration=ProrationDetailsResponse(
            unspent_credit=result.proration.unspent_credit.amount,
            new_plan_charge=result.proration.new_plan_charge.amount,
            net_amount_due=result.proration.net_amount_due.amount,
            remaining_days=result.proration.remaining_days,
            total_period_days=result.proration.total_period_days,
        ),
    )


@router.get("/{subscription_id}/invoices", response_model=List[InvoiceResponse])
def list_invoices(
    subscription_id: str,
    container: ServiceContainer = Depends(get_container),
) -> List[InvoiceResponse]:
    invoices = container.invoice_repo.list_by_subscription(subscription_id)
    return [_serialize_invoice(inv) for inv in invoices]
