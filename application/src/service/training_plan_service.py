from __future__ import annotations

from datetime import datetime, timezone
import json
import re

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.model.training_plan import (
    TrainingPlanCreate,
    TrainingPlanUpdate,
    TrainingPlanScheduleItem,
)


class InvalidQueryError(ValueError):
    pass


class InvalidFieldsError(ValueError):
    pass


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

    if "_id" in out and isinstance(out["_id"], ObjectId):
        out["_id"] = str(out["_id"])

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


def _parse_query(query_str: str | None) -> dict:
    if not query_str or not query_str.strip():
        return {}
    try:
        parsed = json.loads(query_str)
        if not isinstance(parsed, dict):
            raise InvalidQueryError("Query must be a valid JSON object")
        return parsed
    except json.JSONDecodeError as exc:
        raise InvalidQueryError(f"Invalid JSON syntax in query: {str(exc)}")


def _parse_projection(fields: str | None) -> dict | None:
    if not fields or not fields.strip():
        return None

    projection = {}
    pattern = re.compile(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*$")

    for field in fields.split(","):
        clean_field = field.strip()
        if not pattern.match(clean_field):
            raise InvalidFieldsError(f"Invalid MongoDB projection syntax: '{field}'")
        projection[clean_field] = 1

    return projection


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
    db: AsyncDatabase, plan_id: str, *, user_id: str | None = None, fields: str | None = None
) -> dict | None:
    query: dict = {"_id": _require_object_id(plan_id, field_name="plan_id")}
    if user_id is not None:
        query["user_id"] = user_id

    projection = _parse_projection(fields)
    doc = await db.training_plans.find_one(query, projection)
    return _serialize_training_plan(doc)


async def list_training_plans(
    db: AsyncDatabase,
    *,
    user_id: str | None = None,
    query_str: str | None = None,
    fields: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> list[dict]:
    filters = _parse_query(query_str)
    if user_id is not None:
        filters["user_id"] = user_id

    projection = _parse_projection(fields)
    skip = (page - 1) * limit

    cursor = (
        db.training_plans.find(filters, projection)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

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
