import sys
import os

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from mangum import Adapter

# Create handler for AWS Lambda (which Vercel uses)
handler = Adapter(app) 