import sys
import os
import logging

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
    
    # Import the app and create handler
    from main import app
    from mangum import Adapter
    
    # Create handler for AWS Lambda (which Vercel uses)
    handler = Adapter(app)
    
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
        return {
            'statusCode': 500,
            'body': f'Backend initialization error: {str(e)}'
        } 