from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class WorkoutSet(BaseModel):
    reps: int = Field(ge=1)
    weight: float = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class WorkoutExercise(BaseModel):
    exercise_id: str
    order: int = Field(ge=1)
    sets: list[WorkoutSet]

    model_config = ConfigDict(extra="forbid")

    @field_validator("exercise_id")
    @classmethod
    def validate_exercise_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid exercise_id")
        return value


class WorkoutCreate(BaseModel):
    name: str
    exercises: list[WorkoutExercise]

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    exercises: Optional[list[WorkoutExercise]] = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class WorkoutResponse(BaseModel):
    workout_id: Optional[str] = Field(default=None, validation_alias=AliasChoices("_id", "workout_id"))
    user_id: Optional[str] = None
    name: Optional[str] = None
    exercises: Optional[list[WorkoutExercise]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @field_validator("workout_id", mode="before")
    @classmethod
    def convert_object_id(cls, value) -> Optional[str]:
        if isinstance(value, ObjectId):
            return str(value)
        return value
