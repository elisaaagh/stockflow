
from fastapi import FastAPI

from api.routers.products import router as products_router


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

app = FastAPI(
    title="StockFlow API",
    description="REST API for inventory management.",
    version="2.0.0"
)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def root():
    return {
        "application": "StockFlow API",
        "version": "2.0.0",
        "message": "Welcome to StockFlow API"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "stockflow-api"
    }


# ==========================================
# REGISTER ROUTERS
# ==========================================

app.include_router(products_router)
