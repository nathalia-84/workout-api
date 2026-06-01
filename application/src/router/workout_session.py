from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.core.dependencies import get_db
from src.model.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionResponse,
    WorkoutSessionUpdate,
)
from src.service.workout_session_service import (
    complete_session as complete_session_service,
    create_session as create_session_service,
    delete_session as delete_session_service,
    get_session as get_session_service,
    list_sessions as list_sessions_service,
    pause_session as pause_session_service,
    resume_session as resume_session_service,
)

router = APIRouter(
    prefix="/workout-sessions",
    tags=["workout-session"],
)


def _handle_not_found(exc: ValueError) -> HTTPException:
    msg = str(exc)
    if "Invalid" in msg:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


def _handle_state(exc: ValueError) -> HTTPException:
    msg = str(exc)
    if "Invalid" in msg:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


@router.post("/", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(payload: WorkoutSessionCreate, db=Depends(get_db)):
    return await create_session_service(db, payload)


@router.get("/", response_model=list[WorkoutSessionResponse])
async def list_sessions(db=Depends(get_db)):
    return await list_sessions_service(db)


@router.get("/{session_id}", response_model=WorkoutSessionResponse)
async def get_session(session_id: str, db=Depends(get_db)):
    try:
        return await get_session_service(db, session_id)
    except ValueError as exc:
        raise _handle_not_found(exc)


@router.patch("/{session_id}/pause", response_model=WorkoutSessionResponse)
async def pause_session(session_id: str, payload: WorkoutSessionUpdate, db=Depends(get_db)):
    try:
        return await pause_session_service(db, session_id, payload)
    except ValueError as exc:
        raise _handle_state(exc)


@router.patch("/{session_id}/resume", response_model=WorkoutSessionResponse)
async def resume_session(session_id: str, payload: WorkoutSessionUpdate, db=Depends(get_db)):
    try:
        return await resume_session_service(db, session_id, payload)
    except ValueError as exc:
        raise _handle_state(exc)


@router.patch("/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_session(session_id: str, payload: WorkoutSessionUpdate, db=Depends(get_db)):
    try:
        return await complete_session_service(db, session_id, payload)
    except ValueError as exc:
        raise _handle_state(exc)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db=Depends(get_db)):
    try:
        await delete_session_service(db, session_id)
    except ValueError as exc:
        raise _handle_not_found(exc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
