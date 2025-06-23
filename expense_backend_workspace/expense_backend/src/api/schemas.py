"""
Pydantic schemas for API data validation and documentation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date


# ---------------- User Schemas ----------------
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password")
    full_name: Optional[str] = Field(None, description="Full name of user")


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------- Category Schemas ----------------
class CategoryCreate(BaseModel):
    name: str = Field(..., description="Category name")
    color: Optional[str] = Field("#cccccc", description="Category color")


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str


# ---------------- Expense Schemas ----------------
class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, description="Expense description")
    date: date
    category_id: int


class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: Optional[str]
    date: date
    category: CategoryOut


# ---------------- Summary and Analytics ----------------
class MonthlySummary(BaseModel):
    month: str = Field(..., description="Month in YYYY-MM format")
    total_amount: float
    by_category: List[dict]
