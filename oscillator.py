# generating signals and send via bot

import time
import asyncio

from config import Portfolio, FeishuConf
from gateway import Gateway
from feishu_bot import FeishuBot


class Oscillator():

    symbols = Portfolio.symbols
    if 'IXIC' in symbols:
        symbols.remove('IXIC')
    if 'INX' in symbols:
        symbols.remove('INX')

    g = Gateway()
    bot = FeishuBot(FeishuConf.app_id, FeishuConf.app_secret)

    def __init__(self, debug=False):
        self.DEBUG = debug

    def _serialize_time(self, quotation: dict) -> list:
        result = [float(i) for i in quotation]
        result.sort()
        return result

    def _get_price_by_timestamp(self, quotation, ts) -> float:
        result = None
        try:
            result = float(quotation[str(ts)])
        except KeyError:
            debug_info = f'no timestamp give, will look for nearest price for '
            if self.DEBUG:
                print(f'{debug_info}{time.ctime()}')
            time_list = self._serialize_time(quotation)
            key = self._get_nearest_ts(time_list, time.time())
            result = float(quotation[str(key)])
        return result

    def _get_nearest_ts(self, time_list: list, ts_given: float) -> float:
        time_list.sort()
        result = None
        if ts_given > time_list[-1]:
            result = time_list[-1]
        elif ts_given < time_list[0]:
            result = time_list[0]
        else:
            d = 0
            for t in time_list:
                if not d:
                    d = ts_given - t
                if abs(ts_given - t) < d:
                    d = ts_given - t
                    result = t
        return result

    async def do_job(self):
        try:
            for symbol in self.symbols:
                if self.DEBUG:
                    print(f'doing {symbol}')
                quotation = await self.g.hgetall(f'{symbol}_price')
                self.catch_quick_v(quotation)
                
        except Exception:
            raise Exception(f'do_job for {symbol} failed')

    def get_avg_price(self, quotation: dict, mins: int=5):
        '''
        :return: 
        '''
        result = None
        time_list = self._serialize_time(quotation)
        # this causes result varies alongwith time passing
        now = time.time()
        keys = [i for i in time_list if i > now - (60 * mins)]
        if keys:
            prices = [quotation[str(i)] for i in keys]
            try:
                prices = [float(i) for i in prices]
                result = sum(prices) / len(prices)
            except TypeError:
                raise Exception('data type error!')
        return result


    def catch_quick_v(self, quotation) -> str:
        '''
        '''
        debug_info = []
        time_list = self._serialize_time(quotation)
        current_price = self._get_price_by_timestamp(quotation, time.time())
        debug_info.append(f'current price: {current_price}')
        last_5mins_avg = self.get_avg_price(quotation, mins=5)
        debug_info.append(f'last 5 mins avg price: {last_5mins_avg}')
        last_60mins_avg = self.get_avg_price(quotation, mins=60)
        debug_info.append(f'last 60 mins avg price: {last_60mins_avg}')

        if self.DEBUG:
            for info in debug_info:
                print(info)

        # accept ratios when init
        if current_price < last_5mins_avg * 0.999:
            print(f'\n quick v appears! \n')

if if __name__ == "__main__":
    while True:
        o = Oscillator()
        await o.do_job()
        time.sleep(10)
