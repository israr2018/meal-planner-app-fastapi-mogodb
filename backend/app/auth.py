# app/auth.py
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.schemas import TokenData,UserInDB
from app.config import settings
from app.database import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        id: str = payload.get("sub")
        print("payload:", payload)
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(id=token_data.id)
    print("user",user)
    if user is None:
        raise credentials_exception
    return user

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

# async def get_user(username: str):
#     user = await db.family_members.find_one({
#         "$or": [
#             {"username": username},
#             {"email": username}
#         ]
#     })
#     return user
async def get_user(id: str):
    print("id==>",id)
    user = await db.family_members.find_one({
        "_id":ObjectId(id)
    })
    return user
