from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import companies, contacts
from .create_dummy_data import create_dummy_data

app = FastAPI(
    title="PingCRM API",
    description="A CRM system API built with FastAPI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])

@app.get("/")
async def root():
    return {"message": "Welcome to PingCRM API"}

# Initialize the database with dummy data
@app.on_event("startup")
async def startup_event():
    create_dummy_data()
