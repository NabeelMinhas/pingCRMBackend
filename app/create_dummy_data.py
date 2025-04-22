from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Company, Contact
from app.core.database import SessionLocal, engine, Base
import sqlalchemy as sa

def create_dummy_data():
    # Instead of just creating tables if they don't exist,
    # we'll drop all tables and recreate them to ensure our schema is up to date
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have companies
        inspector = sa.inspect(engine)
        if inspector.has_table("companies"):
            company_count = db.query(sa.func.count(Company.id)).scalar()
            if company_count > 0:
                print("Database already has data. Skipping dummy data creation.")
                return
        
        # Create companies
        companies = [
            Company(
                name="Acme Corporation",
                email="info@acme.com",
                phone="555-123-4567",
                address="123 Main St",
                city="New York",
                region="NY",
                country="USA",
                postal_code="10001"
            ),
            Company(
                name="Globex Corporation",
                email="info@globex.com",
                phone="555-234-5678",
                address="456 Elm St",
                city="Los Angeles",
                region="CA",
                country="USA",
                postal_code="90001"
            ),
            Company(
                name="Initech",
                email="info@initech.com",
                phone="555-345-6789",
                address="789 Oak St",
                city="Chicago",
                region="IL",
                country="USA",
                postal_code="60007"
            ),
            Company(
                name="Sirius Cybernetics Corp",
                email="info@sirius.com",
                phone="555-456-7890",
                address="42 Galaxy Way",
                city="San Francisco",
                region="CA",
                country="USA",
                postal_code="94110"
            ),
            Company(
                name="Wayne Enterprises",
                email="info@wayne.com",
                phone="555-567-8901",
                address="1 Wayne Manor",
                city="Gotham",
                region="NJ",
                country="USA",
                postal_code="07101"
            )
        ]
        
        db.add_all(companies)
        db.commit()
        
        # Create contacts
        contacts = [
            Contact(
                first_name="John",
                last_name="Doe",
                email="john.doe@acme.com",
                phone="555-111-2222",
                address="123 Main St",
                city="New York",
                region="NY",
                country="USA",
                postal_code="10001",
                company_id=1
            ),
            Contact(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@globex.com",
                phone="555-222-3333",
                address="456 Elm St",
                city="Los Angeles",
                region="CA",
                country="USA",
                postal_code="90001",
                company_id=2
            ),
            Contact(
                first_name="Michael",
                last_name="Johnson",
                email="michael.johnson@initech.com",
                phone="555-333-4444",
                address="789 Oak St",
                city="Chicago",
                region="IL",
                country="USA",
                postal_code="60007",
                company_id=3
            ),
            Contact(
                first_name="Emily",
                last_name="Brown",
                email="emily.brown@sirius.com",
                phone="555-444-5555",
                address="42 Galaxy Way",
                city="San Francisco",
                region="CA",
                country="USA",
                postal_code="94110",
                company_id=4
            ),
            Contact(
                first_name="Bruce",
                last_name="Wayne",
                email="bruce.wayne@wayne.com",
                phone="555-555-6666",
                address="1 Wayne Manor",
                city="Gotham",
                region="NJ",
                country="USA",
                postal_code="07101",
                company_id=5
            )
        ]
        
        db.add_all(contacts)
        db.commit()
        
        print("Dummy data created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data() 