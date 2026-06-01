from __future__ import annotations

from datetime import datetime, timezone
import json

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.model.workout import WorkoutCreate, WorkoutExercise, WorkoutUpdate


class InvalidQueryError(ValueError):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_object_id(value: str, *, field_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError(f"Invalid {field_name}")
    return ObjectId(value)


def _dump_exercises(exercises: list[WorkoutExercise]) -> list[dict]:
    return [
        {
            "exercise_id": ObjectId(ex.exercise_id),
            "order": ex.order,
            "sets": [s.model_dump() for s in ex.sets],
        }
        for ex in exercises
    ]


def _serialize_workout(doc: dict) -> dict:
    if not doc:
        return doc

    out = {**doc}

    exercises = out.get("exercises")
    if isinstance(exercises, list):
        serialized_exercises: list[dict] = []
        for ex in exercises:
            ex_out = {**ex}
            if isinstance(ex_out.get("exercise_id"), ObjectId):
                ex_out["exercise_id"] = str(ex_out["exercise_id"])
            serialized_exercises.append(ex_out)
        out["exercises"] = serialized_exercises

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


async def create_workout(
    db: AsyncDatabase, payload: WorkoutCreate, *, user_id: str | None = None
) -> dict:
    now = _utc_now()

    doc: dict = {
        "name": payload.name,
        "exercises": _dump_exercises(payload.exercises),
        "created_at": now,
        "updated_at": now,
    }
    if user_id is not None:
        doc["user_id"] = user_id

    result = await db.workouts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_workout(doc)


async def list_workouts(
    db: AsyncDatabase, *, user_id: str | None = None, query_str: str | None = None, limit: int = 100
) -> list[dict]:
    filters = _parse_query(query_str)

    if user_id is not None:
        filters["user_id"] = user_id

    cursor = db.workouts.find(filters).sort("created_at", -1).limit(limit)
    items: list[dict] = []
    async for doc in cursor:
        items.append(_serialize_workout(doc))
    return items


async def get_workout(
    db: AsyncDatabase, workout_id: str, *, user_id: str | None = None
) -> dict | None:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")
    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.workouts.find_one(query)
    return _serialize_workout(doc) if doc else None


async def update_workout(
    db: AsyncDatabase,
    workout_id: str,
    payload: WorkoutUpdate,
    *,
    user_id: str | None = None,
) -> dict | None:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")

    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        return await get_workout(db, workout_id, user_id=user_id)

    if "exercises" in update_data:
        update_data["exercises"] = _dump_exercises(payload.exercises or [])

    update_data["updated_at"] = _utc_now()

    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.workouts.find_one_and_update(
        query,
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return _serialize_workout(doc) if doc else None


async def delete_workout(
    db: AsyncDatabase, workout_id: str, *, user_id: str | None = None
) -> bool:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")
    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    result = await db.workouts.delete_one(query)
    return result.deleted_count == 1
