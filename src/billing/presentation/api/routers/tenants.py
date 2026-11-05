from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from billing.domain.entities import Tenant
from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.schemas import CreateTenantRequest, TenantResponse

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    req: CreateTenantRequest,
    container: ServiceContainer = Depends(get_container),
) -> TenantResponse:
    tenant = Tenant(
        id=f"tenant-{uuid.uuid4().hex[:8]}",
        name=req.name,
        currency=req.currency,
    )
    container.tenant_repo.save(tenant)
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        currency=tenant.currency,
        created_at=tenant.created_at,
        is_active=tenant.is_active,
    )


@router.get("", response_model=List[TenantResponse])
def list_tenants(
    container: ServiceContainer = Depends(get_container),
) -> List[TenantResponse]:
    tenants = container.tenant_repo.list_all()
    return [
        TenantResponse(
            id=t.id,
            name=t.name,
            currency=t.currency,
            created_at=t.created_at,
            is_active=t.is_active,
        )
        for t in tenants
    ]


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: str,
    container: ServiceContainer = Depends(get_container),
) -> TenantResponse:
    tenant = container.tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found",
        )
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        currency=tenant.currency,
        created_at=tenant.created_at,
        is_active=tenant.is_active,
    )
