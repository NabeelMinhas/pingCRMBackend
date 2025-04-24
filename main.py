from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Import modules with error handling
    from app.routers import contacts, companies
    from app.database import engine, Base

    # Create database tables - only on traditional servers, not in serverless
    # Skip in production/Vercel environment
    is_vercel = os.environ.get("VERCEL") == "1"
    if not is_vercel:
        logger.info("Not in Vercel, creating database tables")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Running in Vercel, skipping database table creation")

    app = FastAPI(
        title="PingCRM API",
        description="A CRM system API built with FastAPI",
        version="1.0.0"
    )

    # Configure CORS
    frontend_url = os.environ.get("FRONTEND_URL", "*")
    logger.info(f"Frontend URL: {frontend_url}")
    
    allowed_origins = [frontend_url]
    if "," in frontend_url:
        allowed_origins = frontend_url.split(",")
    
    logger.info(f"Allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    # Include routers
    app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
    app.include_router(companies.router, prefix="/api/companies", tags=["companies"])

    @app.get("/")
    async def root():
        return {"message": "Welcome to PingCRM API", "environment": "Vercel" if is_vercel else "Local"}

    @app.get("/debug")
    async def debug():
        """Endpoint for debugging server configuration"""
        return {
            "environment": os.environ.get("VERCEL", "Not Vercel"),
            "python_version": os.sys.version,
            "allowed_origins": allowed_origins,
            "database_type": "PostgreSQL" if os.environ.get("DATABASE_URL") else "SQLite",
        }

except Exception as e:
    # If there's an error during startup, create a minimal app that returns the error
    logger.error(f"Startup error: {str(e)}", exc_info=True)
    
    app = FastAPI(title="PingCRM API [ERROR]")
    
    @app.get("/")
    async def error_root():
        return {"error": str(e), "message": "The application failed to start properly"} 