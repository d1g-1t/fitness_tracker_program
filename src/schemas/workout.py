from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from src.models.models import WorkoutType


class WorkoutBase(BaseModel):
    workout_type: WorkoutType
    duration_minutes: float = Field(..., gt=0, le=1440)
    distance_km: Optional[float] = Field(None, ge=0)
    average_heart_rate: Optional[int] = Field(None, ge=30, le=250)
    max_heart_rate: Optional[int] = Field(None, ge=30, le=250)
    steps: Optional[int] = Field(None, ge=0)
    pool_length_m: Optional[float] = Field(None, gt=0)
    pool_laps: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    started_at: datetime


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    workout_type: Optional[WorkoutType] = None
    duration_minutes: Optional[float] = Field(None, gt=0, le=1440)
    distance_km: Optional[float] = Field(None, ge=0)
    average_heart_rate: Optional[int] = Field(None, ge=30, le=250)
    max_heart_rate: Optional[int] = Field(None, ge=30, le=250)
    steps: Optional[int] = Field(None, ge=0)
    pool_length_m: Optional[float] = Field(None, gt=0)
    pool_laps: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    calories_burned: Optional[float]
    avg_speed_kmh: Optional[float]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkoutStats(BaseModel):
    total_workouts: int
    total_duration_minutes: float
    total_distance_km: float
    total_calories_burned: float
    average_heart_rate: Optional[float]
    favorite_workout_type: Optional[str]
