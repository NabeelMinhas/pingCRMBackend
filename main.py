from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import contacts, companies
from app.database import engine, Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database tables - only on traditional servers, not in serverless
# Skip in production/Vercel environment
is_vercel = os.environ.get("VERCEL") == "1"
if not is_vercel:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PingCRM API",
    description="A CRM system API built with FastAPI",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.environ.get("FRONTEND_URL", "*")
allowed_origins = [frontend_url]
if "," in frontend_url:
    allowed_origins = frontend_url.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])

@app.get("/")
async def root():
    return {"message": "Welcome to PingCRM API"} 