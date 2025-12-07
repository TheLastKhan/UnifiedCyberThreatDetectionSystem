"""
FastAPI Main Application

Core API setup with CORS, middleware, error handling, and route registration.
"""

import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.api.schemas import ErrorResponse, HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FastAPI App Initialization ====================

app = FastAPI(
    title="Unified Cyber Threat Detection API",
    description="AI-Powered Email & Web Security Analysis API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ==================== CORS Configuration ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Custom Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to response headers."""
    request_id = request.headers.get("x-request-id", str(datetime.utcnow().timestamp()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


# ==================== Exception Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "status_code": 422,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Health Check ====================

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check API and database health status"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthCheckResponse: API and database status
    """
    try:
        from src.database import test_db_connection
        db_status = "ok" if test_db_connection() else "error"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
    
    overall_status = "ok" if db_status == "ok" else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        version="1.0.0"
    )


# ==================== Root Endpoint ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Unified Cyber Threat Detection API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# ==================== Tags Metadata ====================

tags_metadata = [
    {
        "name": "Health",
        "description": "API health check endpoints"
    },
    {
        "name": "Emails",
        "description": "Email phishing detection and analysis"
    },
    {
        "name": "WebLogs",
        "description": "Web server log analysis and anomaly detection"
    },
    {
        "name": "Correlations",
        "description": "Threat correlation between emails and web logs"
    },
    {
        "name": "Reports",
        "description": "Threat analysis reports and statistics"
    },
]

app.openapi_tags = tags_metadata


# ==================== Startup & Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database and resources on startup."""
    logger.info("Application starting up...")
    try:
        from src.database import init_db, test_db_connection
        
        # Initialize database if needed
        # Uncomment for first run:
        # init_db()
        
        # Test database connection
        if test_db_connection():
            logger.info("✓ Database connection successful")
        else:
            logger.warning("⚠ Database connection test failed")
    
    except Exception as e:
        logger.error(f"Startup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Application shutting down...")
    try:
        from src.database import DatabaseEngine
        engine = DatabaseEngine()
        engine.dispose()
        logger.info("✓ Database connections disposed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# ==================== Route Registration ====================

# Import and include routers (will be created)
try:
    from src.api.routes import emails, weblogs, correlations, reports
    
    app.include_router(
        emails.router,
        prefix="/api/emails",
        tags=["Emails"]
    )
    
    app.include_router(
        weblogs.router,
        prefix="/api/weblogs",
        tags=["WebLogs"]
    )
    
    app.include_router(
        correlations.router,
        prefix="/api/correlations",
        tags=["Correlations"]
    )
    
    app.include_router(
        reports.router,
        prefix="/api/reports",
        tags=["Reports"]
    )
    
    logger.info("✓ All routers registered successfully")

except ImportError as e:
    logger.warning(f"Routes not yet implemented: {e}")


# ==================== Application Info ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
