#!/usr/bin/env python
"""
This script tests the FastAPI endpoints by running a local server and 
making requests to it. It's a more comprehensive test than test_vercel.py.
"""

import os
import sys
import time
import threading
import subprocess
import requests
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000"
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

def start_server():
    """Start the FastAPI server in a subprocess"""
    # Set environment variables
    env = os.environ.copy()
    env["VERCEL"] = "1"
    env["DATABASE_URL"] = "postgresql://fake_user:fake_password@fake_host:5432/fake_db"
    
    # Start the server
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Return the process so we can terminate it later
    return process

def wait_for_server(url: str, retries: int = MAX_RETRIES) -> bool:
    """Wait for the server to start responding"""
    for i in range(retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                logger.info(f"Server is up and running after {i+1} attempts")
                return True
        except requests.RequestException:
            logger.info(f"Waiting for server to start (attempt {i+1}/{retries})...")
            time.sleep(RETRY_DELAY)
    
    logger.error(f"Server did not respond after {retries} attempts")
    return False

def test_root_endpoint() -> bool:
    """Test the root endpoint"""
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Root endpoint: {data}")
            return True
        else:
            logger.error(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing root endpoint: {e}")
        return False

def test_debug_endpoint() -> bool:
    """Test the debug endpoint"""
    try:
        response = requests.get(f"{API_URL}/debug")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Debug endpoint: {data}")
            return True
        else:
            logger.error(f"❌ Debug endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing debug endpoint: {e}")
        return False

def main():
    """Run the tests"""
    logger.info("Starting API test...")
    
    # Start the server
    server_process = start_server()
    logger.info("Server started. Waiting for it to be ready...")
    
    # Wait for the server to start
    server_ready = wait_for_server(f"{API_URL}/")
    
    if not server_ready:
        logger.error("Server did not start properly. Exiting.")
        server_process.terminate()
        sys.exit(1)
    
    # Run the tests
    tests = [
        ("Root endpoint", test_root_endpoint),
        ("Debug endpoint", test_debug_endpoint),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        if not test_func():
            all_passed = False
    
    # Clean up
    logger.info("Terminating server...")
    server_process.terminate()
    
    if all_passed:
        logger.info("All API tests passed!")
        print("\n✅ Your backend API is working correctly and ready for Vercel deployment.")
    else:
        logger.error("Some API tests failed!")
        print("\n❌ Your backend API has issues that need to be fixed before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main() 