# app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.meal_plans import generate_weekly_meal_plan
from app.database import db
from datetime import datetime

from app.crud import get_all_family_members

scheduler = AsyncIOScheduler()
async def update_meal_plan():
    print("Updating meal plans for all family members...")
    family_members = await get_all_family_members()
    
    for member in family_members:
        meal_plan = await generate_weekly_meal_plan(member)
        await db.meal_plans.update_one(
            {
                "user_id": member.id,
            },
            {
                "$set": {
                    "days": [day.dict() for day in meal_plan.days],
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
         upsert=True  # Creates new document if doesn't exist
)
        

def schedule_meal_plan_updates():
    # Every Sunday at 12:00 AM PKT (UTC+5)
    scheduler.add_job(
        update_meal_plan,
        # CronTrigger(minute="*", timezone="UTC")
    )
    scheduler.start()
    

# CronTrigger(day_of_week="sun", hour=19, minute=0, timezone="UTC")  # 19:00 UTC = 00:00 PKT