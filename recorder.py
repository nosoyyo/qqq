import time
import redis
import asyncio
from datetime import datetime

from snaper import Snaper
from config import Portfolio


class Recorder():

    # PRODUCTION redis db#15 = Market.US
    # LOCALHOST redis db#15 = [debug]Market.US
    cpool = redis.ConnectionPool(host='localhost', port=6379,
                                 decode_responses=True, db=15)
    r = redis.Redis(connection_pool=cpool)

    async def record(self):
        flag = False
        print(f'{time.ctime()} recording...')
        
        sn = Snaper(Portfolio.symbols)
        await sn.snap()
        for symbol in sn.result:
            price = sn.result[symbol]['current_price']
            net_change = sn.result[symbol]['net_change']
            amp_change = sn.result[symbol]['amp_change']
            volume = sn.result[symbol]['volume']
            amount = sn.result[symbol]['amount']
            ts = time.time()
            try:
                self.r.hset(f'{symbol}_price', ts, price)
                self.r.hset(f'{symbol}_net_change', ts, net_change)
                self.r.hset(f'{symbol}_amp_change', ts, amp_change)
                self.r.hset(f'{symbol}_volume', ts, volume)
                self.r.hset(f'{symbol}_amount', ts, amount)
                flag = True
            except Exception:
                raise Exception(f'rpush{{{symbol}}} failed in Recorder.record()')
        print(flag)

async def main():
    while True:
        recorder = Recorder()
        now = datetime.now()
        if not 3 < now.hour < 16:
            await recorder.record()
            time.sleep(20)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
