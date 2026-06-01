from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.core.dependencies import get_db
from src.model.training_plan import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
)
from src.service.training_plan_service import (
    InvalidFieldsError,
    InvalidQueryError,
    create_training_plan as create_training_plan_service,
    delete_training_plan as delete_training_plan_service,
    get_training_plan as get_training_plan_service,
    list_training_plans as list_training_plans_service,
    update_training_plan as update_training_plan_service,
)


router = APIRouter(
    prefix="/training-plans",
    tags=["training-plan"],
)


@router.post(
    "/",
    response_model=TrainingPlanResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def create_training_plan(payload: TrainingPlanCreate, db=Depends(get_db)):
    try:
        return await create_training_plan_service(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )


@router.get(
    "/",
    response_model=list[TrainingPlanResponse],
    response_model_exclude_none=True,
)
async def list_training_plans(
    query: str | None = Query(None),
    fields: str | None = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=500),
    db=Depends(get_db)
):
    try:
        return await list_training_plans_service(
            db, query_str=query, fields=fields, page=page, limit=limit
        )
    except InvalidQueryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    except InvalidFieldsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )


@router.get(
    "/{plan_id}",
    response_model=TrainingPlanResponse,
    response_model_exclude_none=True,
)
async def get_training_plan(plan_id: str, fields: str | None = Query(None), db=Depends(get_db)):
    try:
        plan = await get_training_plan_service(db, plan_id, fields=fields)
    except InvalidFieldsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found"
        )

    return plan


@router.patch(
    "/{plan_id}",
    response_model=TrainingPlanResponse,
    response_model_exclude_none=True,
)
async def update_training_plan(
    plan_id: str, payload: TrainingPlanUpdate, db=Depends(get_db)
):
    try:
        plan = await update_training_plan_service(db, plan_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found"
        )

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_plan(plan_id: str, db=Depends(get_db)):
    try:
        deleted = await delete_training_plan_service(db, plan_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
