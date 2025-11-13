from redis import asyncio as aioredis
from app.core.config import settings
import json
from typing import Any, Optional

class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        if not self.redis:
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        if not self.redis:
            return
        await self.redis.delete(key)
    
    async def ping(self):
        if not self.redis:
            raise Exception("Redis not connected")
        return await self.redis.ping()

redis_client = RedisClient()
