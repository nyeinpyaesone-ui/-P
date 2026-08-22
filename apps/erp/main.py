"""
ERP03 v1.0.0 - Main Application Entry Point
Modular Monolith Architecture with Event-Driven Capabilities
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import module routers
try:
    from apps.erp.modules.finance.router import router as finance_router
    from apps.erp.modules.hcm.router import router as hcm_router
    from apps.erp.modules.scm.router import router as scm_router
    from apps.erp.modules.mfg.router import router as mfg_router
    from apps.erp.modules.crm.router import router as crm_router
    MODULES_LOADED = True
except ImportError:
    MODULES_LOADED = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connections
    yield
    # Shutdown: Close DB connections
    pass

app = FastAPI(
    title="ERP03 Enterprise System",
    version="1.0.0",
    description="Core ERP modules: Finance, HCM, SCM, Manufacturing, CRM",
    lifespan=lifespan
)

# CORS Configuration - Restrictive defaults for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_methods = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH").split(",")
allowed_headers = os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# Register Modules if available
if MODULES_LOADED:
    app.include_router(finance_router, prefix="/api/v1/finance", tags=["Finance"])
    app.include_router(hcm_router, prefix="/api/v1/hcm", tags=["HCM"])
    app.include_router(scm_router, prefix="/api/v1/scm", tags=["SCM"])
    app.include_router(mfg_router, prefix="/api/v1/mfg", tags=["Manufacturing"])
    app.include_router(crm_router, prefix="/api/v1/crm", tags=["CRM"])

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "modules": MODULES_LOADED}
