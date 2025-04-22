from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Generic, TypeVar, Dict, Any
from datetime import datetime

# Company schemas
class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = lambda field_name: ''.join(word.capitalize() if i else word for i, word in enumerate(field_name.split('_')))

# Contact schemas
class ContactBase(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")
    company_id: Optional[int] = Field(None, alias="companyId")

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = lambda field_name: ''.join(word.capitalize() if i else word for i, word in enumerate(field_name.split('_')))

# Pagination schemas
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int

# Status response schema for operations like soft delete, restore, etc.
class StatusResponse(BaseModel):
    status: str
    message: str 