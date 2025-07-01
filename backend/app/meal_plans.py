# app/meal_plans.py
from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel
from bson import ObjectId
from datetime import datetime, timedelta
from app.schemas import MealPlanDay, WeeklyMealPlan
from app.database import db
from app.crud import get_all_family_members

VEGETARIAN_MEALS = {
    "breakfast": ["Oatmeal", "Avocado toast", "Smoothie bowl"],
    "lunch": ["Vegetable stir fry", "Quinoa salad", "Lentil soup"],
    "dinner": ["Vegetable curry", "Stuffed peppers", "Pasta primavera"],
    "snacks": ["Fruit", "Yogurt", "Nuts"]
}

GLUTEN_FREE_MEALS = {
    "breakfast": ["Eggs with veggies", "Gluten-free pancakes", "Smoothie"],
    "lunch": ["Grilled chicken salad", "Rice bowls", "Stir fry with tamari"],
    "dinner": ["Grilled fish with veggies", "Beef stew with potatoes", "Quinoa pilaf"],
    "snacks": ["Rice cakes", "Cheese", "Fruit"]
}

DEFAULT_MEALS = {
    "breakfast": ["Pancakes", "Eggs and bacon", "Cereal"],
    "lunch": ["Sandwiches", "Soup and salad", "Pasta"],
    "dinner": ["Grilled chicken", "Pizza", "Tacos"],
    "snacks": ["Chips", "Cookies", "Fruit"]
}
T = TypeVar("T")

class ApiResponse(GenericModel, Generic[T]):
    success: bool
    message: Optional[str]
    data: Optional[T]
    
async def generate_weekly_meal_plan(member):
    restrictions = set(member.dietary_restrictions)
    
    week_start = datetime.utcnow()
    days = []
    
    for day in range(7):
        if "vegetarian" in restrictions:
            meals = VEGETARIAN_MEALS
        elif "gluten-free" in restrictions:
            meals = GLUTEN_FREE_MEALS
        else:
            meals = DEFAULT_MEALS
        
        day_plan = MealPlanDay(
            breakfast=meals["breakfast"][day % len(meals["breakfast"])],
            lunch=meals["lunch"][day % len(meals["lunch"])],
            dinner=meals["dinner"][day % len(meals["dinner"])],
            snacks=meals["snacks"][day % len(meals["snacks"])]
        )
        days.append(day_plan)
    
    return WeeklyMealPlan(days=days)

async def get_my_meal_plan(user_id: ObjectId):
    """Get meal plans for a specific user"""
    try:
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, ObjectId):
            user_id = str(user_id)
            
        # Find all meal plans for this user, sorted by week_start_date (newest first)
        print("1")
        print("type of user_id",type(user_id))
        plan = await db.meal_plans.find_one(
            {"user_id": user_id},
            {"_id": 0}  # Exclude MongoDB _id from results
        )
        print("2",plan)
        # Convert cursor to list and format dates
        # plans = []
        # async for plan in cursor:
        #     # Convert ObjectId back to string if needed
        #     # if 'user_id' in plan and isinstance(plan['user_id'], ObjectId):
        #     #     plan['user_id'] = str(plan['user_id'])
            
        #     print("3")
        #     plans.append(plan)
            
        return plan or {}
        
    except Exception as e:
        print(f"Error fetching meal plans: {e}")
        return []