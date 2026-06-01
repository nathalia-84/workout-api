from pymongo import AsyncMongoClient
from src.core.config import settings

import inspect

client: AsyncMongoClient = None


async def connect_db():
    global client
    client = AsyncMongoClient(settings.mongo_uri)


async def close_db():
    global client
    if client:
        result = client.close()
        if inspect.isawaitable(result):
            await result


def get_database():
    return client[settings.mongo_db_name]
