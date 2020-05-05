# can we hold the DST issue until 2021.3.14 ?
# this thing accepts data from Snapper, then store into Redis

# TODO: need to fix still record on non trade day

import time
import redis
import asyncio
from datetime import datetime
from feishu_bot import FeishuBot

from utils import is_trading
from snapper import Snapper, EndSnapper
from config import Portfolio, FeishuConf


class Recorder():

    # PRODUCTION redis db#15 = Market.US
    # LOCALHOST redis db#15 = [debug]Market.US
    cpool = redis.ConnectionPool(host='localhost', port=6379,
                                 decode_responses=True, db=15)
    r = redis.Redis(connection_pool=cpool)

    def __init__(self):
        self._is_trading = is_trading
        self.IS_TRADING = self._is_trading()

    async def record(self):
        flag = False
        print(f'{time.ctime()} recording...')
        
        sn = Snapper(Portfolio.symbols)
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

    async def record_end_day(self):
        flag = False
        print(f'{time.ctime()} do end day recording...')
        es = EndSnapper()
        data = await es.snap()
        for symbol in data.keys():
            result = {}
            # e.g. 'TSLA_20200428'
            _set = f'{symbol}_{data[symbol]["date"]}'
            _list = data[symbol]["data"]
            _list = [i.split(' ') for i in _list]
            try:
                for i in _list: 
                    # _time be like '0941' => 9:41AM
                    _time = i[0]
                    _price = i[1]
                    _volume = i[2]
                    # e.g. 'ZM_20200504_price
                    self.r.hset(f'{_set}_price', _time, _price)
                    self.r.hset(f'{_set}_volume', _time, _volume)
                    flag = True
            except Exception:
                raise Exception('failed when try save to redis in record_end_day()')
        return flag

async def main():
    while True:
        try:
            recorder = Recorder()
            if recorder.IS_TRADING:
                await recorder.record()
                time.sleep(20)
            else:
                now = datetime.now()
                # do a final record
                await recorder.record()
                # grab stuff from another source
                await recorder.record_end_day()
                
                # un somno tutum!
                dormit = 60
                if now.weekday() < 6:
                    if not recorder.IS_TRADING:
                        dormit = recorder.START.timestamp() - time.time()
                    else:
                        # actually the start of the next trade day
                        next_day = datetime(
                            now.year,
                            now.month,
                            now.day+1,
                            recorder.START.hour,
                            recorder.START.minute
                            )
                        dormit = next_day.timestamp() - time.time()
                else:
                    # see if everything changes tomorrow!
                    dormit = 86400
                next_wake = datetime.fromtimestamp(time.time() + dormit)
                print(f'not trading. will wake on {next_wake}')
                time.sleep(dormit)
        except Exception:
            bot = FeishuBot(FeishuConf.app_id, FeishuConf.app_secret)
            warning = 'Recorder() 异常退出了狸！'
            await bot.send_text(warning, groups=FeishuConf.MSFC)
            raise Exception('unknown exception!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
