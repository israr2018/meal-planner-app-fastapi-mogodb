# app/main.py
from datetime import datetime
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.schemas import FamilyMemberCreate, FamilyMember, WeeklyMealPlan
from app.crud import create_family_member, get_all_family_members,authenticate_user
from app.meal_plans import ApiResponse, generate_weekly_meal_plan,get_my_meal_plan
from app.auth import get_current_user, create_access_token
from app.scheduler import schedule_meal_plan_updates
from app.config import settings
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm  # Add this import
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    schedule_meal_plan_updates()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Meal Planning API",
    description="API for the Meal Planning Web App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register_user(member: FamilyMemberCreate):
   member_id = await create_family_member(member)
   return {"id": member_id}


@app.get("/family-members/", response_model=list[FamilyMember])
async def list_family_members():
    return await get_all_family_members()

@app.get("/meal-plan/my", response_model=WeeklyMealPlan)
async def fetch_my_meal_plan(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    meal_plan = await get_my_meal_plan(user_id)
    days=meal_plan["days"]
    return WeeklyMealPlan(days=days)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Meal Planning API",
        version="1.0.0",
        description="API for the Meal Planning Web App",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Meal Planning API - Swagger UI",
    )