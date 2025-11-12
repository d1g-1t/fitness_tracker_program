from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_workouts_per_week: Optional[int] = Field(None, ge=1, le=50)
    target_calories_per_week: Optional[float] = Field(None, gt=0)
    target_distance_km: Optional[float] = Field(None, gt=0)
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    deadline: Optional[datetime] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_workouts_per_week: Optional[int] = Field(None, ge=1, le=50)
    target_calories_per_week: Optional[float] = Field(None, gt=0)
    target_distance_km: Optional[float] = Field(None, gt=0)
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    deadline: Optional[datetime] = None
    is_achieved: Optional[bool] = None


class GoalResponse(GoalBase):
    id: int
    user_id: int
    is_achieved: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GoalProgress(BaseModel):
    goal_id: int
    goal_title: str
    current_workouts: int
    target_workouts: Optional[int]
    current_calories: float
    target_calories: Optional[float]
    current_distance: float
    target_distance: Optional[float]
    progress_percentage: float
    is_on_track: bool
