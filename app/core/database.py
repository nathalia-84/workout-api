from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.mongo_uri)


async def close_db():
    global client
    if client:
        client.close()


def get_database():
    return client[settings.mongo_db_name]