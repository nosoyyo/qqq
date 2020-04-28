# can we hold the DST issue until 2021.3.14 ?

import time
import redis
import asyncio
from datetime import datetime
from feishu_bot import FeishuBot

from snaper import Snaper
from config import Portfolio, FeishuConf


class Recorder():

    # PRODUCTION redis db#15 = Market.US
    # LOCALHOST redis db#15 = [debug]Market.US
    cpool = redis.ConnectionPool(host='localhost', port=6379,
                                 decode_responses=True, db=15)
    r = redis.Redis(connection_pool=cpool)

    def __init__(self):
        self.IS_TRADING = self._is_trading()

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
                raise Exception(f'hset {symbol} failed in Recorder.record()')
        print(flag)

    def _is_trading(self):
        flag = False
        now = datetime.now()
        if now.weekday() > 5:
            return flag
        if now < datetime(2020, 11, 1):
            self.OVER = datetime(now.year,now.month,now.day,4,0)
            self.START = datetime(now.year,now.month,now.day,21,30)
        else:
            self.OVER = datetime(now.year,now.month,now.day,5,0)
            self.START = datetime(now.year,now.month,now.day,22,30)
        if not self.OVER < now < self.START:
            flag = True
        return flag


async def main():
    while True:
        try:
            recorder = Recorder()
            if recorder.IS_TRADING:
                await recorder.record()
                time.sleep(20)
            else:
                await recorder.record()
                now = datetime.now()
                # un somno tutum!
                dormit = 60
                if now.weekday() < 6:
                    if not recorder.IS_TRADING:
                        # let's do this 66 secs earlier!
                        dormit = recorder.START.timestamp() - time.time() - 66
                    else:
                        next_day = datetime(
                            now.year,
                            now.month,
                            now.day+1,
                            recorder.START.hour,
                            recorder.START.minute
                            )
                        dormit = next_day.timestamp() - time.time() - 66
                else:
                    # see if everything changes tomorrow!
                    dormit = 86400
                next_wake = datetime.fromtimestamp(time.time() + dormit)
                print(f'not trading. will wake on {next_wake}')
                time.sleep(dormit)
        except Exception:
            bot = FeishuBot(FeishuBot.app_id, FeishuBot.app_secret)
            warning = 'Recorder() 异常退出了狸！'
            await bot.send_text(warning, groups=FeishuConf.MSFC)
            raise Exception('unknown exception!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())