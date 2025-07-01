# app/schemas.py
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr,SecretStr,Field
from typing import List, Optional
from enum import Enum
# Add this class for token data
class TokenData(BaseModel):
    id: Optional[str] = None

class DietaryRestriction(str, Enum):
    vegetarian = "vegetarian"
    gluten_free = "gluten-free"
    dairy_free = "dairy-free"
    nut_free = "nut-free"
    none = "none"

class FamilyMemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr  # Using SecretStr for security
    dietary_restrictions: List[DietaryRestriction]

class FamilyMemberDB(BaseModel):
    id: str
    name: str
    email: EmailStr
    hashed_password: str  # Store hashed, not plain text
    dietary_restrictions: List[DietaryRestriction]
    created_at: datetime


class FamilyMember(BaseModel):
    id: str
    dietary_restrictions: List[DietaryRestriction] = []

class MealPlanDay(BaseModel):
    breakfast: str
    lunch: str
    dinner: str
    snacks: str
class DailyMeal(BaseModel):
    breakfast: str
    lunch: str
    dinner: str
    snacks: str


class WeeklyMealPlan(BaseModel):
    days: List[MealPlanDay]

class UserBase(BaseModel):
    email: str
    full_name: str | None = None
    
class UserInDB(UserBase):
    id: str
    disabled: bool | None = None
    dietary_restrictions: list[str] = []