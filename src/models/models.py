from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
import enum
from typing import List


class WorkoutType(str, enum.Enum):
    RUNNING = "running"
    WALKING = "walking"
    SWIMMING = "swimming"
    CYCLING = "cycling"
    STRENGTH = "strength"
    YOGA = "yoga"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    workouts: Mapped[List["Workout"]] = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[List["Goal"]] = relationship(
        "Goal", back_populates="user", cascade="all, delete-orphan"
    )


class Workout(Base):
    __tablename__ = "workouts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    workout_type: Mapped[WorkoutType] = mapped_column(Enum(WorkoutType), nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    
    calories_burned: Mapped[float] = mapped_column(Float, nullable=True)
    average_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    
    steps: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_speed_kmh: Mapped[float] = mapped_column(Float, nullable=True)
    
    pool_length_m: Mapped[float] = mapped_column(Float, nullable=True)
    pool_laps: Mapped[int] = mapped_column(Integer, nullable=True)
    
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship("User", back_populates="workouts")
    
    __table_args__ = (
        Index("ix_workouts_user_started", "user_id", "started_at"),
        Index("ix_workouts_type_started", "workout_type", "started_at"),
    )


class Goal(Base):
    __tablename__ = "goals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    target_workouts_per_week: Mapped[int] = mapped_column(Integer, nullable=True)
    target_calories_per_week: Mapped[float] = mapped_column(Float, nullable=True)
    target_distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    target_weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_achieved: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    user: Mapped["User"] = relationship("User", back_populates="goals")
