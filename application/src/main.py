from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.router.training_plan import router as training_plan_router
from src.router.workout import router as workout_router
from src.core.database import close_db, connect_db
from src.router.health import router as health_router
from src.router.auth import router as auth_router


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
app.include_router(auth_router)
app.include_router(workout_router, prefix="/api")
app.include_router(training_plan_router, prefix="/api")
