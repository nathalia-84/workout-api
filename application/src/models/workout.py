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

<<<<<<< HEAD:app/models/workout.py
    model_config = ConfigDict(extra="forbid")

    @field_validator("exercise_id")
    @classmethod
    def validate_exercise_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid exercise_id")
        return value

=======
>>>>>>> cbbdfae (chore: create major top structuring dirs):application/src/models/workout.py

class WorkoutCreate(BaseModel):
    name: str
    exercises: list[WorkoutExercise]

<<<<<<< HEAD:app/models/workout.py
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

=======
>>>>>>> cbbdfae (chore: create major top structuring dirs):application/src/models/workout.py

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    exercises: Optional[list[WorkoutExercise]] = None

<<<<<<< HEAD:app/models/workout.py
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

=======
>>>>>>> cbbdfae (chore: create major top structuring dirs):application/src/models/workout.py

class WorkoutResponse(BaseModel):
    workout_id: str = Field(validation_alias=AliasChoices("_id", "workout_id"))
    user_id: Optional[str] = None
    name: str
    exercises: list[WorkoutExercise]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @field_validator("workout_id", mode="before")
    @classmethod
    def convert_object_id(cls, value) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        return value
