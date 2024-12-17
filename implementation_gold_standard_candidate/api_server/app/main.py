import logging

from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import LoggingMiddleware
from app.api.v1 import flight
from app.core.logging import setup_logging
from app.core.database import Database
from app.core.cors import setup_cors
app = FastAPI()
# Add CORS middleware
app.add_middleware(LoggingMiddleware)

setup_logging()
# Include routers
app.include_router(
    flight.router,
    prefix="/api/v1/flight",
    tags=["flight"]
)

setup_cors(app)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize MongoDB
        await Database.init_mongodb()
        
        # Initialize Redis
        await Database.init_redis()
        
        logging.info("All database connections initialized successfully")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await Database.close_mongodb_connection()
        Database.close_redis_connection()
        logging.info("All database connections closed successfully")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to the Flight API"}

