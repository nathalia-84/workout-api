from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import close_db, connect_db
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Workout API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
