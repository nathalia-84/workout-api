from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

class TrainingPlanScheduleItem(BaseModel):
    weekday: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    workout_id: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("workout_id")
    @classmethod
    def validate_workout_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid workout_id")
        return value

class TrainingPlanCreate(BaseModel):
    name: str
    schedule: list[TrainingPlanScheduleItem]

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TrainingPlanUpdate(BaseModel):
    name: Optional[str] = None
    schedule: Optional[list[TrainingPlanScheduleItem]] = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TrainingPlanResponse(BaseModel):
    plan_id: str = Field(validation_alias=AliasChoices("_id", "plan_id"))
    user_id: Optional[str] = None
    name: str
    schedule: list[TrainingPlanScheduleItem]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @field_validator("plan_id", mode="before")
    @classmethod
    def convert_object_id(cls, value) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        return value

