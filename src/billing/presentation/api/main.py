from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from billing.presentation.api.routers import billing, plans, subscriptions, tenants


def create_app() -> FastAPI:
    app = FastAPI(
        title="Multi-Tenant Subscription & Billing Engine",
        description="Clean Architecture billing engine with prorated plan switching, usage metering, and fault-tolerant charges.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Basic CORS support
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers under /api/v1
    app.include_router(tenants.router, prefix="/api/v1")
    app.include_router(plans.router, prefix="/api/v1")
    app.include_router(subscriptions.router, prefix="/api/v1")
    app.include_router(billing.router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "service": "billing-engine"}

    @app.get("/", tags=["Health"])
    def root():
        return {
            "name": "Multi-Tenant Subscription & Billing Engine",
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app


app = create_app()
