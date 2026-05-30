from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from app.models.workout import WorkoutCreate, WorkoutExercise, WorkoutUpdate


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_object_id(value: str, *, field_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError(f"Invalid {field_name}")
    return ObjectId(value)


def _dump_exercises(exercises: list[WorkoutExercise]) -> list[dict]:
    dumped: list[dict] = []
    for ex in exercises:
        exercise_oid = _require_object_id(ex.exercise_id, field_name="exercise_id")
        dumped.append(
            {
                "exercise_id": exercise_oid,
                "order": ex.order,
                "sets": [s.model_dump() for s in ex.sets],
            }
        )
    return dumped


def _serialize_workout(doc: dict) -> dict:
    if not doc:
        return doc

    out = {**doc}
    if "_id" in out:
        out["id"] = str(out.pop("_id"))

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


async def create_workout(db, payload: WorkoutCreate, *, user_id: str | None = None) -> dict:
    now = _utc_now_iso()

    doc: dict = {
        "user_id": user_id,
        "name": payload.name,
        "exercises": _dump_exercises(payload.exercises),
        "created_at": now,
        "updated_at": now,
    }
    if user_id is None:
        doc.pop("user_id", None)

    result = await db.workouts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_workout(doc)


async def list_workouts(db, *, user_id: str | None = None, limit: int = 100) -> list[dict]:
    query: dict = {}
    if user_id is not None:
        query["user_id"] = user_id

    cursor = db.workouts.find(query).sort("created_at", -1).limit(limit)
    items: list[dict] = []
    async for doc in cursor:
        items.append(_serialize_workout(doc))
    return items


async def get_workout(db, workout_id: str, *, user_id: str | None = None) -> dict | None:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")
    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.workouts.find_one(query)
    return _serialize_workout(doc) if doc else None


async def update_workout(
    db,
    workout_id: str,
    payload: WorkoutUpdate,
    *,
    user_id: str | None = None,
) -> dict | None:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")

    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        # Nothing to change; return the current document untouched.
        return await get_workout(db, workout_id, user_id=user_id)

    if "exercises" in update_data:
        # Re-validate and convert referenced exercise ids to ObjectId.
        update_data["exercises"] = _dump_exercises(payload.exercises or [])

    update_data["updated_at"] = _utc_now_iso()

    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.workouts.find_one_and_update(
        query,
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return _serialize_workout(doc) if doc else None


async def delete_workout(db, workout_id: str, *, user_id: str | None = None) -> bool:
    workout_oid = _require_object_id(workout_id, field_name="workout_id")
    query: dict = {"_id": workout_oid}
    if user_id is not None:
        query["user_id"] = user_id

    result = await db.workouts.delete_one(query)
    return result.deleted_count == 1
