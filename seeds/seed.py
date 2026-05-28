import asyncio
from src.app.core.database import connect_db, close_db, get_database
from seeds.data import muscle_groups, exercises


async def seed():
    # 1. Initialize the connection
    await connect_db()
    db = get_database()

    try:
        # 2. Clear existing data
        await db.muscle_groups.delete_many({})
        await db.exercises.delete_many({})

        # 3. Insert new data
        await db.muscle_groups.insert_many(muscle_groups)
        await db.exercises.insert_many(exercises)

        print("Database seeded successfully.")
    finally:
        # 4. Clean up the connection
        await close_db()

if __name__ == "__main__":
    asyncio.run(seed())
