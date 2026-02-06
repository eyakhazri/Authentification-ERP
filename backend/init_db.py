import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["users"]
    
    # Check if admin exists
    existing = await db.admin.find_one({"email": "GourmEase@gmail.com"})
    
    if existing:
        print("Admin already exists!")
        return
    
    # Create default admin
    admin = {
        "email": "gourmease@gmail.com",
        "hashed_password": pwd_context.hash("SECRET123"),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    await db.admin.insert_one(admin)
    print("Default admin created:")
    print("Email: gourmease@gmail.com")
    print("Password: SECRET123")
    print("IMPORTANT: Change this password after first login!")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(init_database())