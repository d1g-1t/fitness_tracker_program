import redis.asyncio as aioredis
from src.core.config import settings
from typing import Optional
import json
from datetime import timedelta


class CacheService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[timedelta] = None,
    ) -> bool:
        if not self.redis:
            return False
        
        if expire:
            await self.redis.setex(key, expire, value)
        else:
            await self.redis.set(key, value)
        return True

    async def delete(self, key: str) -> bool:
        if not self.redis:
            return False
        await self.redis.delete(key)
        return True

    async def get_json(self, key: str) -> Optional[dict]:
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: dict,
        expire: Optional[timedelta] = None,
    ) -> bool:
        return await self.set(key, json.dumps(value), expire)


cache_service = CacheService()
