# app/crud.py
from typing import List
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException,status
from app.database import db
from app.schemas import FamilyMember, FamilyMemberCreate
from datetime import datetime
from bson import ObjectId
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from app.schemas import UserInDB

async def get_family_member(member_id: str):
    member = await db.family_members.find_one({"_id": ObjectId(member_id)})
    if member:
        member["id"] = str(member["_id"])
        return FamilyMember(**member)
    return None

# async def get_all_family_members():
#     members = []
#     async for member in db.family_members.find():
#         members.append({"id": str(member["_id"]),  # Convert ObjectId to string
#             "dietary_restrictions": member["dietary_restrictions"]})
#     return members


async def get_all_family_members():
    members = []
    async for doc in db.family_members.find(
        {},
        {
            "dietary_restrictions": 1,
            "_id": 1
        }
    ):
        members.append(FamilyMember(
            id=str(doc["_id"]),
            dietary_restrictions=doc.get("dietary_restrictions", [])
        ))
    return members

async def create_family_member(member: FamilyMemberCreate):
    """
    Creates a new family member with proper error handling
    """
    try:
        # Check if email already exists
        existing_member = await db.family_members.find_one({"email": member.email})
        if existing_member:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = pwd_context.hash(member.password.get_secret_value())
        
        # Create member document
        db_member = {
            "name": member.name,
            "email": member.email,
            "hashed_password": hashed_password,
            "dietary_restrictions": member.dietary_restrictions,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.family_members.insert_one(db_member)
        if not result.inserted_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create member"
            )
            
        return str(result.inserted_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )
    
async def authenticate_user(username: str, password: str):
    """
    Authenticates a user by verifying username and password
    
    Args:
        username: str - The username/email to authenticate
        password: str - The plaintext password to verify
        
    Returns:
        UserInDB: The authenticated user if successful
        None: If authentication fails
        
    Raises:
        HTTPException: If user not found or password invalid
    """
    # 1. Find user in database
    user = await db.family_members.find_one({"$or": [
        {"username": username},
        {"email": username}
    ]})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verify password
    if not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Return user data (without password hash)
    return UserInDB(
        id=str(user["_id"]),
        username=user.get("username", user["email"]),
        email=user["email"],
        full_name=user["name"],
        disabled=user.get("disabled", False),
        dietary_restrictions=user.get("dietary_restrictions", [])
    )