from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import get_db
from app.models.training_plan import (
    TrainingPlanCreate,
    TrainingPlanResponse,
    TrainingPlanUpdate,
)
from app.services.training_plan_service import (
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

# TODO: the service layer already scopes every query by `user_id`, but it is
# never passed here. Inject the authenticated user (e.g. Depends(get_current_user))
# and forward it to enforce per-user ownership before this is exposed publicly.

@router.post("/", response_model=TrainingPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_training_plan(payload: TrainingPlanCreate, db=Depends(get_db)):
    try:
        return await create_training_plan_service(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

@router.get("/", response_model=list[TrainingPlanResponse])
async def list_training_plans(db=Depends(get_db)):
    return await list_training_plans_service(db)

@router.get("/{plan_id}", response_model=TrainingPlanResponse)
async def get_training_plan(plan_id: str, db=Depends(get_db)):
    try:
        plan = await get_training_plan_service(db, plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found")

    return plan

@router.patch("/{plan_id}", response_model=TrainingPlanResponse)
async def update_training_plan(plan_id: str, payload: TrainingPlanUpdate, db=Depends(get_db)):
    try:
        plan = await update_training_plan_service(db, plan_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found")

    return plan

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_plan(plan_id: str, db=Depends(get_db)):
    try:
        deleted = await delete_training_plan_service(db, plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training plan not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
