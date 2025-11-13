from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate, WorkoutStats
from src.services.workout_service import WorkoutService
from src.api.dependencies import get_current_user
from src.models.models import User, WorkoutType
from typing import List, Optional
from src.core.logging import get_logger
from src.core.cache import cache_service
from datetime import timedelta
import json


logger = get_logger(__name__)
router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Создание тренировки для пользователя: ID {current_user.id}")
    
    workout = await WorkoutService.create_workout(db, current_user.id, workout_data)
    await db.commit()
    
    await cache_service.delete(f"user:{current_user.id}:workouts")
    await cache_service.delete(f"user:{current_user.id}:stats")
    
    return workout


@router.get("", response_model=List[WorkoutResponse])
async def get_workouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    workout_type: Optional[WorkoutType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"user:{current_user.id}:workouts:{skip}:{limit}:{workout_type}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"Получение тренировок из кэша для пользователя: ID {current_user.id}")
        return json.loads(cached)
    
    workouts = await WorkoutService.get_user_workouts(
        db, current_user.id, skip, limit, workout_type
    )
    
    result = [WorkoutResponse.model_validate(w) for w in workouts]
    
    await cache_service.set(
        cache_key,
        json.dumps([r.model_dump(mode="json") for r in result], default=str),
        expire=timedelta(minutes=5),
    )
    
    return result


@router.get("/stats", response_model=WorkoutStats)
async def get_workout_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"user:{current_user.id}:stats:{days}"
    
    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"Получение статистики из кэша для пользователя: ID {current_user.id}")
        return WorkoutStats(**json.loads(cached))
    
    stats = await WorkoutService.get_workout_statistics(db, current_user.id, days)
    
    await cache_service.set(
        cache_key,
        json.dumps(stats.model_dump()),
        expire=timedelta(minutes=10),
    )
    
    return stats


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workout = await WorkoutService.get_workout_by_id(db, workout_id, current_user.id)
    
    if not workout:
        logger.warning(f"Тренировка не найдена: ID {workout_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )
    
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_data: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_workout = await WorkoutService.update_workout(
        db, workout_id, current_user.id, workout_data
    )
    
    if not updated_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )
    
    await db.commit()
    
    await cache_service.delete(f"user:{current_user.id}:workouts")
    await cache_service.delete(f"user:{current_user.id}:stats")
    
    return updated_workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await WorkoutService.delete_workout(db, workout_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )
    
    await db.commit()
    
    await cache_service.delete(f"user:{current_user.id}:workouts")
    await cache_service.delete(f"user:{current_user.id}:stats")
