from typing import Optional

from pydantic import BaseModel

class WorkoutSet(BaseModel):
    reps: int
    weight: float

class WorkoutExercise(BaseModel):
    exercise_id: str
    order: int
    sets: list[WorkoutSet]

class WorkoutCreate(BaseModel):
    name: str
    exercises: list[WorkoutExercise]

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    exercises: Optional[list[WorkoutExercise]] = None

class WorkoutResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    exercises: list[WorkoutExercise]
    created_at: str
    updated_at: str
