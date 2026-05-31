from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.model.training_plan import (
    TrainingPlanCreate,
    TrainingPlanUpdate,
    TrainingPlanScheduleItem,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_object_id(value: str, *, field_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError(f"Invalid {field_name}")
    return ObjectId(value)


def _dump_schedule(schedule: list[TrainingPlanScheduleItem]) -> list[dict]:
    return [
        {
            "weekday": item.weekday,
            "workout_id": ObjectId(item.workout_id),
        }
        for item in schedule
    ]


def _serialize_training_plan(doc: dict) -> dict:
    if not doc:
        return doc

    out = {**doc}

    schedule = out.get("schedule")
    if isinstance(schedule, list):
        serialized_schedule: list[dict] = []
        for item in schedule:
            item_out = {**item}
            if isinstance(item_out.get("workout_id"), ObjectId):
                item_out["workout_id"] = str(item_out["workout_id"])
            serialized_schedule.append(item_out)
        out["schedule"] = serialized_schedule

    return out


async def create_training_plan(
    db: AsyncDatabase, payload: TrainingPlanCreate, *, user_id: str | None = None
) -> dict:
    now = _utc_now()

    doc: dict = {
        "name": payload.name,
        "schedule": _dump_schedule(payload.schedule),
        "created_at": now,
        "updated_at": now,
    }
    if user_id is not None:
        doc["user_id"] = user_id

    result = await db.training_plans.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_training_plan(doc)


async def get_training_plan(
    db: AsyncDatabase, plan_id: str, *, user_id: str | None = None
) -> dict | None:
    query: dict = {"_id": _require_object_id(plan_id, field_name="plan_id")}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.training_plans.find_one(query)
    return _serialize_training_plan(doc)


async def list_training_plans(
    db: AsyncDatabase, *, user_id: str | None = None
) -> list[dict]:
    query = {}
    if user_id is not None:
        query["user_id"] = user_id

    cursor = db.training_plans.find(query).sort("created_at", -1)
    plans = []
    async for doc in cursor:
        plans.append(_serialize_training_plan(doc))
    return plans


async def update_training_plan(
    db: AsyncDatabase,
    plan_id: str,
    payload: TrainingPlanUpdate,
    *,
    user_id: str | None = None,
) -> dict | None:
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        return await get_training_plan(db, plan_id, user_id=user_id)

    update_doc: dict = {"updated_at": _utc_now()}
    if payload.name is not None:
        update_doc["name"] = payload.name
    if payload.schedule is not None:
        update_doc["schedule"] = _dump_schedule(payload.schedule)

    query: dict = {"_id": _require_object_id(plan_id, field_name="plan_id")}
    if user_id is not None:
        query["user_id"] = user_id

    updated_doc = await db.training_plans.find_one_and_update(
        query,
        {"$set": update_doc},
        return_document=ReturnDocument.AFTER,
    )
    return _serialize_training_plan(updated_doc)


async def delete_training_plan(
    db: AsyncDatabase, plan_id: str, *, user_id: str | None = None
) -> bool:
    query: dict = {"_id": _require_object_id(plan_id, field_name="plan_id")}
    if user_id is not None:
        query["user_id"] = user_id

    result = await db.training_plans.delete_one(query)
    return result.deleted_count > 0
