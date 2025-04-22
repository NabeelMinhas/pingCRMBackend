from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import Company
from app import schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=schemas.PaginatedResponse[schemas.Company])
def get_companies(
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None,
    status: str = "active",
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(Company)
    
    # Apply status filter
    if status == "active":
        query = query.filter(Company.deleted_at == None)
    elif status == "trashed":
        query = query.filter(Company.deleted_at != None)
    # "all" status doesn't need filtering
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            or_(
                Company.name.ilike(f"%{search}%"),
                Company.email.ilike(f"%{search}%"),
                Company.city.ilike(f"%{search}%"),
                Company.phone.ilike(f"%{search}%")
            )
        )
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    companies = query.offset(skip).limit(limit).all()
    
    return {
        "items": companies,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.get("/{company_id}", response_model=schemas.Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.put("/{company_id}", response_model=schemas.Company)
def update_company(
    company_id: int,
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Don't allow updating deleted companies
    if db_company.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Cannot update a deleted company")
    
    for key, value in company.model_dump().items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

@router.patch("/{company_id}/soft-delete", response_model=schemas.StatusResponse)
def soft_delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if already deleted
    if company.deleted_at is not None:
        return {"status": "warning", "message": "Company is already deleted"}
    
    # Perform soft delete
    company.deleted_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "Company has been moved to trash"}

@router.patch("/{company_id}/restore", response_model=schemas.Company)
def restore_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if not deleted
    if company.deleted_at is None:
        raise HTTPException(status_code=400, detail="Company is not in trash")
    
    # Restore company
    company.deleted_at = None
    db.commit()
    db.refresh(company)
    
    return company

@router.delete("/{company_id}", response_model=schemas.StatusResponse)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return {"status": "success", "message": "Company permanently deleted"} 