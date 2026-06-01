from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.core.dependencies import get_current_user, get_db
from src.model.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate
from src.service.workout_service import (
    InvalidFieldsError,
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
async def create_workout(
    payload: WorkoutCreate,
    db=Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        return await create_workout_service(db, payload, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )


@router.get("/", response_model=list[WorkoutResponse], response_model_exclude_none=True)
async def list_workouts(
    query: str | None = Query(None),
    fields: str | None = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=500),
    db=Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        return await list_workouts_service(
            db, query_str=query, fields=fields, page=page, limit=limit, user_id=user_id
        )
    except InvalidQueryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    except InvalidFieldsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )


@router.get("/{workout_id}", response_model=WorkoutResponse, response_model_exclude_none=True)
async def get_workout(
    workout_id: str,
    fields: str | None = Query(None),
    db=Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        workout = await get_workout_service(db, workout_id, fields=fields, user_id=user_id)
    except InvalidFieldsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
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
async def update_workout(
    workout_id: str,
    payload: WorkoutUpdate,
    db=Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        workout = await update_workout_service(db, workout_id, payload, user_id=user_id)
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
async def delete_workout(
    workout_id: str,
    db=Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    try:
        deleted = await delete_workout_service(db, workout_id, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
