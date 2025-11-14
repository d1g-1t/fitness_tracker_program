from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from src.models.models import Workout, User, WorkoutType
from src.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutStats
from src.services.analytics import CalorieCalculator, WorkoutAnalytics
from typing import Optional, List
from datetime import datetime, timedelta
from src.core.logging import get_logger


logger = get_logger(__name__)


class WorkoutService:
    
    @staticmethod
    async def create_workout(
        db: AsyncSession, user_id: int, workout_data: WorkoutCreate
    ) -> Workout:
        logger.info(f"Создание новой тренировки для пользователя: ID {user_id}")
        
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"Пользователь не найден: ID {user_id}")
            raise ValueError("Пользователь не найден")
        
        avg_speed = None
        if workout_data.distance_km and workout_data.duration_minutes:
            avg_speed = WorkoutAnalytics.calculate_average_speed(
                workout_data.distance_km, workout_data.duration_minutes
            )
        
        distance_km = workout_data.distance_km
        if workout_data.workout_type == WorkoutType.SWIMMING and workout_data.pool_length_m and workout_data.pool_laps:
            distance_km = WorkoutAnalytics.calculate_swimming_distance(
                workout_data.pool_length_m, workout_data.pool_laps
            )
        
        calories_burned = None
        if user.weight:
            calories_burned = CalorieCalculator.calculate_calories(
                workout_data.workout_type,
                workout_data.duration_minutes,
                user.weight,
                avg_speed,
            )
        
        steps = workout_data.steps
        if not steps and distance_km:
            steps = WorkoutAnalytics.estimate_steps(distance_km, workout_data.workout_type)
        
        workout = Workout(
            user_id=user_id,
            workout_type=workout_data.workout_type,
            duration_minutes=workout_data.duration_minutes,
            distance_km=distance_km,
            calories_burned=calories_burned,
            avg_speed_kmh=avg_speed,
            average_heart_rate=workout_data.average_heart_rate,
            max_heart_rate=workout_data.max_heart_rate,
            steps=steps,
            pool_length_m=workout_data.pool_length_m,
            pool_laps=workout_data.pool_laps,
            notes=workout_data.notes,
            started_at=workout_data.started_at,
            completed_at=workout_data.started_at + timedelta(minutes=workout_data.duration_minutes),
        )
        
        db.add(workout)
        await db.flush()
        await db.refresh(workout)
        
        logger.info(f"Тренировка создана успешно: ID {workout.id}")
        return workout
    
    @staticmethod
    async def get_workout_by_id(
        db: AsyncSession, workout_id: int, user_id: int
    ) -> Optional[Workout]:
        result = await db.execute(
            select(Workout).where(
                and_(Workout.id == workout_id, Workout.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_workouts(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        workout_type: Optional[WorkoutType] = None,
    ) -> List[Workout]:
        query = select(Workout).where(Workout.user_id == user_id)
        
        if workout_type:
            query = query.where(Workout.workout_type == workout_type)
        
        query = query.order_by(desc(Workout.started_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_workout(
        db: AsyncSession, workout_id: int, user_id: int, workout_data: WorkoutUpdate
    ) -> Optional[Workout]:
        logger.info(f"Обновление тренировки: ID {workout_id}")
        
        workout = await WorkoutService.get_workout_by_id(db, workout_id, user_id)
        if not workout:
            logger.warning(f"Тренировка не найдена: ID {workout_id}")
            return None
        
        update_data = workout_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(workout, field, value)
        
        if workout.distance_km and workout.duration_minutes:
            workout.avg_speed_kmh = WorkoutAnalytics.calculate_average_speed(
                workout.distance_km, workout.duration_minutes
            )
        
        await db.flush()
        await db.refresh(workout)
        
        logger.info(f"Тренировка обновлена успешно: ID {workout_id}")
        return workout
    
    @staticmethod
    async def delete_workout(db: AsyncSession, workout_id: int, user_id: int) -> bool:
        logger.info(f"Удаление тренировки: ID {workout_id}")
        
        workout = await WorkoutService.get_workout_by_id(db, workout_id, user_id)
        if not workout:
            logger.warning(f"Тренировка не найдена: ID {workout_id}")
            return False
        
        await db.delete(workout)
        logger.info(f"Тренировка удалена успешно: ID {workout_id}")
        return True
    
    @staticmethod
    async def get_workout_statistics(
        db: AsyncSession, user_id: int, days: int = 30
    ) -> WorkoutStats:
        logger.info(f"Получение статистики тренировок для пользователя: ID {user_id}")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(
                func.count(Workout.id).label("total_workouts"),
                func.sum(Workout.duration_minutes).label("total_duration"),
                func.coalesce(func.sum(Workout.distance_km), 0).label("total_distance"),
                func.coalesce(func.sum(Workout.calories_burned), 0).label("total_calories"),
                func.avg(Workout.average_heart_rate).label("avg_heart_rate"),
            ).where(
                and_(
                    Workout.user_id == user_id,
                    Workout.started_at >= start_date,
                )
            )
        )
        
        stats = result.one()
        
        type_result = await db.execute(
            select(Workout.workout_type, func.count(Workout.id).label("count"))
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.started_at >= start_date,
                )
            )
            .group_by(Workout.workout_type)
            .order_by(desc("count"))
            .limit(1)
        )
        
        favorite_type = type_result.first()
        
        return WorkoutStats(
            total_workouts=stats.total_workouts or 0,
            total_duration_minutes=float(stats.total_duration or 0),
            total_distance_km=float(stats.total_distance or 0),
            total_calories_burned=float(stats.total_calories or 0),
            average_heart_rate=float(stats.avg_heart_rate) if stats.avg_heart_rate else None,
            favorite_workout_type=favorite_type[0].value if favorite_type else None,
        )
