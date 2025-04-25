from mangum import Mangum
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
    
    # Create the Mangum handler for AWS Lambda/Vercel
    handler = Mangum(app)
    
except Exception as e:
    from fastapi import FastAPI
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"Error initializing Vercel handler: {str(e)}", exc_info=True)
    
    # Fallback app that returns the error
    app = FastAPI(title="PingCRM API [ERROR]")
    
    @app.get("/")
    async def error_root():
        return {"error": str(e), "message": "The serverless function failed to initialize properly"}
    
    handler = Mangum(app)
