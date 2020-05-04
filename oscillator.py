# generating signals and send via bot

import time
import asyncio

from utils import lify
from gateway import Gateway
from feishu_bot import FeishuBot
from config import Portfolio, FeishuConf


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
        '''
        no return
        only send text via bot if any
        '''
        try:
            result = {}
            for symbol in self.symbols:
                if self.DEBUG:
                    print(f'doing {symbol}')
                quotation = await self.g.hgetall(f'{symbol}_price')
                info = self.catch_quick_v(quotation, symbol)
                if info:
                    result[symbol] = info
            if result:
                print(result)
                await self.bot.send_text(lify(result), groups=FeishuConf.MSFC)
                
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


    def catch_quick_v(self, quotation: dict, symbol:str) -> dict:
        '''
        '''
        debug_info = []
        result = {}

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
        if current_price < last_5mins_avg * 0.995:
            result.update({'现价低于 5 分钟均价' : f'{1 - current_price / last_5mins_avg:.2%}'})
        elif current_price < last_60mins_avg * 0.995:
            result.update({'现价低于 60 分钟均价' : f'{1 - current_price / last_60mins_avg:.2%}'})
        
        return result


async def main():
    while True:
        o = Oscillator()
        await o.do_job()
        time.sleep(20)


if __name__ == "__main__":
    await main()
