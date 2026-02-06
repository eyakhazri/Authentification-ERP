from motor.motor_asyncio import AsyncIOMotorClient
from src.app.config import settings

client = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]  # MUST be "admin"
    print("✅ Connected to DB:", db.name)
    return db

async def close_db():
    if client:
        client.close()

def get_db():
    return db
