import aioredis
import asyncio


class Redis:
    _redis = None

    async def get_redis_pool(self, *args, **kwargs):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(*args, **kwargs)
        return self._redis

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


class Gateway():

    # PRODUCTION redis db#15 = Market.US
    # LOCALHOST redis db#15 = [debug]Market.US

    async def hgetall(self, key):
        redis = Redis()
        r = await redis.get_redis_pool(
            ('localhost', 6379),
            db=15,
            encoding='utf-8'
            )
        result = await r.hgetall(key)
        await redis.close()      
        return result
