from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.core.dependencies import get_db
from src.model.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate
from src.service.workout_service import (
    InvalidQueryError,
    create_workout as create_workout_service,
    delete_workout as delete_workout_service,
    get_workout as get_workout_service,
    list_workouts as list_workouts_service,
    update_workout as update_workout_service,
)

router = APIRouter(
    prefix="/workouts",
    tags=["workout"],
)


@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
async def create_workout(payload: WorkoutCreate, db=Depends(get_db)):
    try:
        return await create_workout_service(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )


@router.get("/", response_model=list[WorkoutResponse], response_model_exclude_none=True)
async def list_workouts(
    query: str | None = Query(None),
    limit: int = Query(default=100, ge=1, le=500),
    db=Depends(get_db),
):
    try:
        return await list_workouts_service(db, query_str=query, limit=limit)
    except InvalidQueryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )


@router.get("/{workout_id}", response_model=WorkoutResponse, response_model_exclude_none=True)
async def get_workout(workout_id: str, db=Depends(get_db)):
    try:
        workout = await get_workout_service(db, workout_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    return workout


@router.patch("/{workout_id}", response_model=WorkoutResponse, response_model_exclude_none=True)
async def update_workout(workout_id: str, payload: WorkoutUpdate, db=Depends(get_db)):
    try:
        workout = await update_workout_service(db, workout_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if workout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(workout_id: str, db=Depends(get_db)):
    try:
        deleted = await delete_workout_service(db, workout_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
