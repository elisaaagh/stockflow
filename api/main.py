
from fastapi import FastAPI

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
# HEALTH CHECK ENDPOINT
# ==========================================

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "stockflow-api"
    }
