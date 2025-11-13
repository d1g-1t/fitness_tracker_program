from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.goal import GoalCreate, GoalResponse, GoalUpdate, GoalProgress
from src.services.goal_service import GoalService
from src.api.dependencies import get_current_user
from src.models.models import User
from typing import List
from src.core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Создание цели для пользователя: ID {current_user.id}")
    
    goal = await GoalService.create_goal(db, current_user.id, goal_data)
    await db.commit()
    
    return goal


@router.get("", response_model=List[GoalResponse])
async def get_goals(
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goals = await GoalService.get_user_goals(db, current_user.id, active_only)
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await GoalService.get_goal_by_id(db, goal_id, current_user.id)
    
    if not goal:
        logger.warning(f"Цель не найдена: ID {goal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )
    
    return goal


@router.get("/{goal_id}/progress", response_model=GoalProgress)
async def get_goal_progress(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    progress = await GoalService.get_goal_progress(db, goal_id, current_user.id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )
    
    return progress


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_goal = await GoalService.update_goal(db, goal_id, current_user.id, goal_data)
    
    if not updated_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )
    
    await db.commit()
    
    return updated_goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await GoalService.delete_goal(db, goal_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )
    
    await db.commit()
