"""
Trinity Context Core - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from src.api.routes import router as api_router
from src.api.middleware import ContextLoggingMiddleware
from src.core.logger import ContextLogger

# Initialize FastAPI app
app = FastAPI(
    title="Trinity Context Core",
    description="Core backend for Trinity Context system with semantic memory",
    version="0.1.0"
)

# Initialize context logger for middleware
context_logger = ContextLogger()

# Add autonomous logging middleware
app.add_middleware(ContextLoggingMiddleware, logger=context_logger)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/ping")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        dict: Status message indicating the service is operational
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "Trinity Context Core is running",
            "version": "0.1.0"
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint with basic API information.
    
    Returns:
        dict: Welcome message and API details
    """
    return {
        "name": "Trinity Context Core",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/ping",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
