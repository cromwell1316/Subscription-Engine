from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status

from billing.domain.entities import Plan
from billing.domain.exceptions import BillingDomainError
from billing.domain.value_objects import Money
from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.schemas import CreatePlanRequest, PlanResponse

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    req: CreatePlanRequest,
    container: ServiceContainer = Depends(get_container),
) -> PlanResponse:
    tenant = container.tenant_repo.get_by_id(req.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {req.tenant_id} not found",
        )

    try:
        plan = Plan(
            id=f"plan-{uuid.uuid4().hex[:8]}",
            tenant_id=req.tenant_id,
            name=req.name,
            price=Money(amount=req.price, currency=req.currency),
            period=req.period,
            included_units=req.included_units,
            overage_unit_price=Money(amount=req.overage_unit_price, currency=req.currency),
            trial_days=req.trial_days,
        )
        container.plan_repo.save(plan)
    except BillingDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return PlanResponse(
        id=plan.id,
        tenant_id=plan.tenant_id,
        name=plan.name,
        price=plan.price.amount,
        currency=plan.price.currency,
        period=plan.period,
        included_units=plan.included_units,
        overage_unit_price=plan.overage_unit_price.amount if plan.overage_unit_price else req.overage_unit_price,
        trial_days=plan.trial_days,
        is_active=plan.is_active,
        version=plan.version,
    )


@router.get("", response_model=List[PlanResponse])
def list_plans(
    tenant_id: str = Query(..., description="Tenant ID to filter plans"),
    container: ServiceContainer = Depends(get_container),
) -> List[PlanResponse]:
    plans = container.plan_repo.list_by_tenant(tenant_id)
    return [
        PlanResponse(
            id=p.id,
            tenant_id=p.tenant_id,
            name=p.name,
            price=p.price.amount,
            currency=p.price.currency,
            period=p.period,
            included_units=p.included_units,
            overage_unit_price=p.overage_unit_price.amount if p.overage_unit_price else p.price.amount,
            trial_days=p.trial_days,
            is_active=p.is_active,
            version=p.version,
        )
        for p in plans
    ]
