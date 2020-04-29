import json
import aioredis

from starlette.routing import Route
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse


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


async def get_price(symbol):
    redis = Redis()
    r = await redis.get_redis_pool(('127.0.0.1', 6379), db=15, encoding='utf-8')
    result = await r.hgetall(symbol)
    await redis.close()
    return result

async def get_symbol_price(request, debug=True):
    '''
    approx. 12kb for one-day data
    thus it could be very slow when years later
    approx. 3mb for one-year data
    '''
    symbol = request.path_params['symbol']
    symbol = f'{symbol.upper()}_price'
    if debug:
        print(request.path_params)
        print(symbol)
    j = await get_price(symbol)
    return JSONResponse(j)

app = Starlette(debug=True, routes=[
    Route('/symbol/{symbol}/price', get_symbol_price),
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001)
