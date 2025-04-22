from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models import Contact
from app import schemas
from app.core.database import get_db
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=schemas.PaginatedResponse[schemas.Contact])
def get_contacts(
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None,
    company_id: Optional[int] = None,
    status: str = "active",
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(Contact)
    
    # Apply status filter
    if status == "active":
        query = query.filter(Contact.deleted_at == None)
    elif status == "trashed":
        query = query.filter(Contact.deleted_at != None)
    # "all" status doesn't need filtering
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            or_(
                Contact.first_name.ilike(f"%{search}%"),
                Contact.last_name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
                Contact.phone.ilike(f"%{search}%"),
                Contact.city.ilike(f"%{search}%")
            )
        )
    
    # Filter by company if provided
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    contacts = query.offset(skip).limit(limit).all()
    
    return {
        "items": contacts,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.get("/{contact_id}", response_model=schemas.Contact)
def get_contact(
    contact_id: int, 
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db)
):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact.model_dump().items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.delete("/{contact_id}", response_model=schemas.StatusResponse)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Soft delete by setting deleted_at timestamp
    contact.deleted_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Contact deleted successfully"}

@router.post("/{contact_id}/restore", response_model=schemas.StatusResponse)
def restore_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact.deleted_at is None:
        return {"status": "info", "message": "Contact is not deleted"}
    
    # Restore by clearing deleted_at timestamp
    contact.deleted_at = None
    db.commit()
    return {"status": "success", "message": "Contact restored successfully"} 