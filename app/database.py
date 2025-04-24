from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Get database URL from environment variables
    # Default to SQLite for local development but use PostgreSQL in production
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    logger.info(f"Database URL found: {'Yes' if DATABASE_URL else 'No'}")
    
    if not DATABASE_URL:
        # Fallback to SQLite for local development
        DATABASE_URL = "sqlite:///./pingcrm.db"
        logger.info(f"Using SQLite database: {DATABASE_URL}")
        SQLALCHEMY_DATABASE_URL = DATABASE_URL
    else:
        # Handle special case for PostgreSQL URLs from Vercel/Heroku
        # They start with postgres://, but SQLAlchemy requires postgresql://
        if DATABASE_URL.startswith("postgres://"):
            logger.info("Converting postgres:// to postgresql://")
            SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        else:
            SQLALCHEMY_DATABASE_URL = DATABASE_URL
        
        logger.info(f"Using PostgreSQL database: {SQLALCHEMY_DATABASE_URL[:10]}...")

    # Create engine with appropriate parameters
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        logger.info("Adding SQLite-specific connection arguments")
        connect_args = {"check_same_thread": False}

    # Create engine with some additional parameters suitable for serverless
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args=connect_args,
        pool_pre_ping=True,  # Check connection before using from pool
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_size=5,         # Limit pool size for serverless
        max_overflow=10      # Allow 10 more connections than pool_size
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

    # Dependency
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

except Exception as e:
    logger.error(f"Database setup error: {str(e)}", exc_info=True)
    
    # Create dummy base and engine for error cases
    Base = declarative_base()
    engine = None
    
    # Dummy session that will raise the original error when used
    class ErrorSession:
        def __init__(self, error):
            self.error = error
            
        def __enter__(self):
            raise self.error
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    original_error = e
    
    def get_db():
        raise original_error 