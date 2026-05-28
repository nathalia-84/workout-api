from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.dependencies import get_db
from app.models.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate
from app.services.workout_service import (
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

# TODO: the service layer already scopes every query by `user_id`, but it is
# never passed here. Inject the authenticated user (e.g. Depends(get_current_user))
# and forward it to enforce per-user ownership before this is exposed publicly.

@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(payload: WorkoutCreate, db=Depends(get_db)):
    try:
        return await create_workout_service(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

@router.get("/", response_model=list[WorkoutResponse])
async def list_workouts(
    limit: int = Query(default=100, ge=1, le=500),
    db=Depends(get_db),
):
    return await list_workouts_service(db, limit=limit)

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(workout_id: str, db=Depends(get_db)):
    try:
        workout = await get_workout_service(db, workout_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    return workout

@router.patch("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(workout_id: str, payload: WorkoutUpdate, db=Depends(get_db)):
    try:
        workout = await update_workout_service(db, workout_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    return workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(workout_id: str, db=Depends(get_db)):
    try:
        deleted = await delete_workout_service(db, workout_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
