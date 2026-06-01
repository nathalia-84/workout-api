from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.model.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionResponse,
    WorkoutSessionUpdate,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_object_id(value: str, *, field_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError(f"Invalid {field_name}")
    return ObjectId(value)


def _serialize_session(doc: dict) -> WorkoutSessionResponse:
    return WorkoutSessionResponse.model_validate(doc)


async def create_session(
    db: AsyncDatabase, payload: WorkoutSessionCreate, *, user_id: str | None = None
) -> WorkoutSessionResponse:
    now = _utc_now()

    doc: dict = {
        "user_id": user_id,
        "workout_id": ObjectId(payload.workout_id),
        "status": "in_progress",
        "duration_seconds": None,
        "history": [{"from_status": "pending", "to_status": "in_progress", "created_at": now}],
        "notes": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.workout_sessions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_session(doc)


async def list_sessions(
    db: AsyncDatabase, *, user_id: str | None = None
) -> list[WorkoutSessionResponse]:
    query: dict = {}
    if user_id is not None:
        query["user_id"] = user_id

    cursor = db.workout_sessions.find(query).sort("created_at", -1)
    sessions = []
    async for doc in cursor:
        sessions.append(_serialize_session(doc))
    return sessions


async def get_session(
    db: AsyncDatabase, session_id: str, *, user_id: str | None = None
) -> WorkoutSessionResponse:
    session_oid = _require_object_id(session_id, field_name="session_id")
    query: dict = {"_id": session_oid}
    if user_id is not None:
        query["user_id"] = user_id

    doc = await db.workout_sessions.find_one(query)
    if not doc:
        raise ValueError("Session not found")
    return _serialize_session(doc)


async def pause_session(
    db: AsyncDatabase,
    session_id: str,
    payload: WorkoutSessionUpdate,
    *,
    user_id: str | None = None,
) -> WorkoutSessionResponse:
    now = _utc_now()
    session_oid = _require_object_id(session_id, field_name="session_id")

    update_doc: dict = {
        "$set": {"status": "paused", "updated_at": now},
        "$push": {"history": {"from_status": "in_progress", "to_status": "paused", "created_at": now}},
    }
    if payload.notes is not None:
        update_doc["$set"]["notes"] = payload.notes

    query: dict = {"_id": session_oid, "status": "in_progress"}
    if user_id is not None:
        query["user_id"] = user_id

    updated_doc = await db.workout_sessions.find_one_and_update(
        query,
        update_doc,
        return_document=ReturnDocument.AFTER,
    )

    if not updated_doc:
        raise ValueError("Session not found or not in progress")

    return _serialize_session(updated_doc)


async def resume_session(
    db: AsyncDatabase,
    session_id: str,
    payload: WorkoutSessionUpdate,
    *,
    user_id: str | None = None,
) -> WorkoutSessionResponse:
    now = _utc_now()
    session_oid = _require_object_id(session_id, field_name="session_id")

    update_doc: dict = {
        "$set": {"status": "in_progress", "updated_at": now},
        "$push": {"history": {"from_status": "paused", "to_status": "in_progress", "created_at": now}},
    }
    if payload.notes is not None:
        update_doc["$set"]["notes"] = payload.notes

    query: dict = {"_id": session_oid, "status": "paused"}
    if user_id is not None:
        query["user_id"] = user_id

    updated_doc = await db.workout_sessions.find_one_and_update(
        query,
        update_doc,
        return_document=ReturnDocument.AFTER,
    )

    if not updated_doc:
        raise ValueError("Session not found or not paused")

    return _serialize_session(updated_doc)


async def complete_session(
    db: AsyncDatabase,
    session_id: str,
    payload: WorkoutSessionUpdate,
    *,
    user_id: str | None = None,
) -> WorkoutSessionResponse:
    now = _utc_now()
    session_oid = _require_object_id(session_id, field_name="session_id")

    update_doc: dict = {
        "$set": {"status": "completed", "updated_at": now},
        "$push": {"history": {"from_status": "in_progress", "to_status": "completed", "created_at": now}},
    }
    if payload.notes is not None:
        update_doc["$set"]["notes"] = payload.notes

    query: dict = {"_id": session_oid, "status": "in_progress"}
    if user_id is not None:
        query["user_id"] = user_id

    updated_doc = await db.workout_sessions.find_one_and_update(
        query,
        update_doc,
        return_document=ReturnDocument.AFTER,
    )

    if not updated_doc:
        raise ValueError("Session not found or not in progress")

    return _serialize_session(updated_doc)


async def delete_session(
    db: AsyncDatabase, session_id: str, *, user_id: str | None = None
) -> None:
    session_oid = _require_object_id(session_id, field_name="session_id")
    query: dict = {"_id": session_oid}
    if user_id is not None:
        query["user_id"] = user_id

    result = await db.workout_sessions.delete_one(query)
    if result.deleted_count == 0:
        raise ValueError("Session not found")
