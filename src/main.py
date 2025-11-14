from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.cache import cache_service
from src.core.logging import setup_logging, get_logger
from src.api.v1.users import router as users_router
from src.api.v1.workouts import router as workouts_router
from src.api.v1.goals import router as goals_router
from pathlib import Path


Path("logs").mkdir(exist_ok=True)
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения TrackFit Pro API")
    await cache_service.connect()
    logger.info("Подключение к Redis успешно")
    
    yield
    
    logger.info("Остановка приложения TrackFit Pro API")
    await cache_service.disconnect()
    logger.info("Отключение от Redis")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Профессиональный REST API для отслеживания фитнес-активности с расширенной аналитикой",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(workouts_router, prefix=settings.API_V1_PREFIX)
app.include_router(goals_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "TrackFit Pro API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
