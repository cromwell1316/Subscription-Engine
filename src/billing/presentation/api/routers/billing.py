from fastapi import APIRouter, Depends, HTTPException, status

from billing.application.use_cases.record_usage import RecordUsageCommand
from billing.domain.exceptions import BillingDomainError, SubscriptionNotActiveError, TenantMismatchError
from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.schemas import (
    BillingCycleResponse,
    RecordUsageRequest,
    RecordUsageResponse,
)

router = APIRouter(tags=["Billing & Usage"])


@router.post("/usage", response_model=RecordUsageResponse, status_code=status.HTTP_201_CREATED)
def record_usage(
    req: RecordUsageRequest,
    container: ServiceContainer = Depends(get_container),
) -> RecordUsageResponse:
    use_case = container.get_record_usage_use_case()
    cmd = RecordUsageCommand(
        tenant_id=req.tenant_id,
        subscription_id=req.subscription_id,
        metric_name=req.metric_name,
        units=req.units,
    )
    try:
        record = use_case.execute(cmd)
    except (TenantMismatchError, SubscriptionNotActiveError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BillingDomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return RecordUsageResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        subscription_id=record.subscription_id,
        units=record.units,
        recorded_at=record.recorded_at,
    )


@router.post("/billing-cycle/run", response_model=BillingCycleResponse)
def run_billing_cycle(
    container: ServiceContainer = Depends(get_container),
) -> BillingCycleResponse:
    use_case = container.get_run_billing_cycle_use_case()
    result = use_case.execute()

    return BillingCycleResponse(
        renewed_count=len(result.renewed_subscriptions),
        failed_count=len(result.failed_subscriptions),
        renewed_subscriptions=result.renewed_subscriptions,
        failed_subscriptions=result.failed_subscriptions,
        invoices_generated=result.invoices_generated,
    )
