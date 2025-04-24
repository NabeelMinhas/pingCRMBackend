import sys
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Add the parent directory to the path to allow imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Log environment for debugging
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Directory contents: {os.listdir('.')}")
    
    # Set Vercel flag to ensure we skip SQLite operations in serverless
    os.environ["VERCEL"] = "1"
    
    # Try importing the main app with error handling
    try:
        from main import app
        logger.info("Successfully imported main app")
    except ImportError as e:
        logger.error(f"Failed to import main app: {str(e)}")
        
        # Create a minimal API for fallback
        from fastapi import FastAPI
        app = FastAPI(title="PingCRM API [FALLBACK]")
        
        @app.get("/")
        async def fallback_root():
            return {"status": "error", "message": "Main app import failed", "error": str(e)}
    
    # Import mangum correctly
    import mangum
    
    # Create handler for AWS Lambda (which Vercel uses)
    handler = mangum.Mangum(app)
    
    # Simple test function to verify handler works
    def test_handler(event, context):
        return {
            'statusCode': 200,
            'body': 'Handler initialized successfully'
        }
        
except Exception as e:
    logger.error(f"Error in index.py: {str(e)}", exc_info=True)
    
    # Provide a fallback handler that returns the error
    def handler(event, context):
        # Try to create a JSON response
        try:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': str(e),
                    'traceback': str(sys.exc_info())
                })
            }
        except:
            # If JSON serialization fails, return a plain text response
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'text/plain'
                },
                'body': f'Backend initialization error: {str(e)}'
            } 