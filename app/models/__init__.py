# This file makes the models directory a Python package
from app.models.models import User, Organization
from app.models.crm import Company, Contact

__all__ = ["User", "Organization", "Company", "Contact"] 