from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from billing.presentation.api.dependencies import ServiceContainer, get_container

router = APIRouter(prefix="/system", tags=["System Management & Observability"])


@router.get("/stats")
def get_system_stats(
    container: ServiceContainer = Depends(get_container),
) -> Dict[str, Any]:
    return container.get_system_stats()


@router.post("/circuit-breaker/trip")
def trip_circuit_breaker(
    container: ServiceContainer = Depends(get_container),
) -> Dict[str, Any]:
    container.circuit_breaker.trip()
    container.payment_gateway.simulate_transient_failure = True
    return {
        "status": "ok",
        "message": "Simulated bank outage (504 Timeout). Circuit Breaker tripped to OPEN.",
        "circuit_breaker": {
            "state": container.circuit_breaker.state.value,
            "failure_count": container.circuit_breaker.failure_count,
        },
    }


@router.post("/circuit-breaker/reset")
def reset_circuit_breaker(
    container: ServiceContainer = Depends(get_container),
) -> Dict[str, Any]:
    container.circuit_breaker.reset()
    container.payment_gateway.simulate_transient_failure = False
    return {
        "status": "ok",
        "message": "Bank gateway connection restored. Circuit Breaker reset to CLOSED.",
        "circuit_breaker": {
            "state": container.circuit_breaker.state.value,
            "failure_count": container.circuit_breaker.failure_count,
        },
    }


@router.get("/subscriptions")
def list_all_subscriptions(
    container: ServiceContainer = Depends(get_container),
) -> List[Dict[str, Any]]:
    if hasattr(container.subscription_repo, "_subs"):
        subs = list(container.subscription_repo._subs.values())
    else:
        subs = []

    res = []
    for s in subs:
        plan = container.plan_repo.get_by_id(s.plan_id)
        plan_name = plan.name if plan else s.plan_id
        res.append(
            {
                "id": s.id,
                "tenant_id": s.tenant_id,
                "customer_id": s.customer_id,
                "plan_id": s.plan_id,
                "plan_name": plan_name,
                "status": s.status.value,
                "current_period_start": s.current_period_start.isoformat(),
                "current_period_end": s.current_period_end.isoformat(),
                "trial_end": s.trial_end.isoformat() if s.trial_end else None,
                "retry_count": s.retry_count,
            }
        )
    return res


@router.get("/invoices")
def list_all_invoices(
    container: ServiceContainer = Depends(get_container),
) -> List[Dict[str, Any]]:
    if hasattr(container.invoice_repo, "_invoices"):
        invoices = list(container.invoice_repo._invoices.values())
    else:
        invoices = []

    # Sort descending by creation date
    invoices.sort(key=lambda x: x.created_at, reverse=True)

    res = []
    for inv in invoices:
        items_desc = ", ".join(f"{it.description} ({it.total})" for it in inv.line_items)
        res.append(
            {
                "id": inv.id,
                "tenant_id": inv.tenant_id,
                "customer_id": inv.customer_id,
                "subscription_id": inv.subscription_id,
                "status": inv.status.value,
                "currency": inv.currency.value,
                "total_amount": str(inv.total_amount.amount),
                "items_summary": items_desc,
                "created_at": inv.created_at.isoformat(),
                "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
                "failure_reason": inv.failure_reason,
            }
        )
    return res


@router.get("/outbox")
def list_outbox_events(
    container: ServiceContainer = Depends(get_container),
) -> List[Dict[str, Any]]:
    events = []
    if hasattr(container.outbox_repo, "list_all"):
        raw_events = container.outbox_repo.list_all()
    elif hasattr(container.outbox_repo, "_events"):
        raw_events = list(reversed(container.outbox_repo._events))
    else:
        raw_events = container.outbox_repo.list_unpublished(limit=50)

    for e in raw_events:
        events.append(
            {
                "event_id": e.event_id,
                "tenant_id": e.tenant_id,
                "event_type": e.event_type,
                "occurred_at": e.occurred_at.isoformat(),
            }
        )
    return events
