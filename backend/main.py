"""
OpenSeat FastAPI Backend Application
Main entry point for the API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import uvicorn

from src.config.database import init_db
from src.config.settings import get_settings
from src.middleware.error_handler import (
    OpenSeatException,
    openseat_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler
)

# Import routes
from src.routes.auth_routes import router as auth_router
from src.routes.route_routes import router as route_router
from src.routes.booking_routes import router as booking_router
from src.routes.payment_routes import router as payment_router
from src.routes.vehicle_routes import router as vehicle_router

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OpenSeat - Community-powered micro-ridesharing platform for daily work commutes",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(OpenSeatException, openseat_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routers
app.include_router(auth_router)
app.include_router(route_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(vehicle_router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    """
    print("🚀 Starting OpenSeat API...")
    print(f"📊 Initializing database...")
    init_db()
    print("✅ Database initialized successfully")


@app.get("/")
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Welcome to OpenSeat API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
