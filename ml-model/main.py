import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status

from routers import recommendations, interactions
from database.interactions import DBInteractions
from config.settings import (
    ALLOWED_ORIGINS, 
    APP_TITLE, 
    APP_DESCRIPTION, 
    APP_VERSION
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with additional metadata
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration with more explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Access-Control-Allow-Headers", 
        "Access-Control-Allow-Origin"
    ]
)

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """
    Custom handler for HTTP exceptions to provide consistent error responses
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": str(exc.detail)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Custom handler for request validation errors
    """
    errors = exc.errors()
    error_details = [
        {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        } for error in errors
    ]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Validation error",
            "details": error_details
        }
    )

# Corrected lifecycle events using proper FastAPI event decorators
@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    - Initialize database connection pool
    - Perform any necessary startup tasks
    """
    try:
        await DBInteractions.init_pool()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    - Close database connection pool
    - Perform cleanup tasks
    """
    try:
        await DBInteractions.close_pool()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")

# Include Routers with improved organization
app.include_router(
    recommendations.router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"]
)
app.include_router(
    interactions.router,
    prefix="/api/v1/interactions",
    tags=["Interactions"]
)

# Health check endpoint with more detailed information
@app.get("/health", tags=["System"])
async def health_check():
    """
    Endpoint for service health check
    
    Returns:
    - Basic system status
    - Database connection status
    """
    try:
        # You could add more comprehensive health checks here
        return {
            "status": "healthy",
            "version": APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }

# Optional: Additional startup logging
logger.info(f"Application {APP_TITLE} (v{APP_VERSION}) initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # Run with: uvicorn main:app --reload