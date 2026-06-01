from datetime import datetime
from typing import Literal, Optional

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

SessionStatus = Literal["pending", "in_progress", "paused", "completed"]

class SessionHistoryItem(BaseModel):
    from_status: SessionStatus
    to_status: SessionStatus
    created_at: datetime

class WorkoutSessionCreate(BaseModel):
    workout_id: str
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("workout_id")
    @classmethod
    def validate_workout_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid workout_id")
        return value

class WorkoutSessionUpdate(BaseModel):
    notes: Optional[str] = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class WorkoutSessionResponse(BaseModel):
    session_id: str = Field(validation_alias=AliasChoices("_id", "session_id"))
    user_id: Optional[str] = None
    workout_id: Optional[str] = None
    status: SessionStatus = "in_progress"
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    history: list[SessionHistoryItem] = Field(default_factory=list)
    notes: Optional[str] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    @field_validator("session_id", "user_id", "workout_id", mode="before")
    @classmethod
    def convert_object_id(cls, value) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        return value
