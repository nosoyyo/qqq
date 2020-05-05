# generating signals and send via bot

import time
import asyncio

from gateway import Gateway
from feishu_bot import FeishuBot
from utils import lify, is_trading
from datamodel import BaseDictFormat
from config import Portfolio, FeishuConf


class Oscillator(BaseDictFormat):

    symbols = Portfolio.symbols
    if 'IXIC' in symbols:
        symbols.remove('IXIC')
    if 'INX' in symbols:
        symbols.remove('INX')

    g = Gateway()
    bot = FeishuBot(FeishuConf.app_id, FeishuConf.app_secret)

    def __init__(self, debug=False):
        self.DEBUG = debug
        self._is_trading = is_trading
        self.IS_TRADING = self._is_trading()

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
                if self.DEBUG:
                    print(result)
                volume = await self.g.hgetall(f'{symbol}_volume')
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
        current_price = self._read_ts_dict(quotation, time.time())
        debug_info.append(f'current price: {current_price}')
        last_5mins_avg = self.get_avg_price(quotation, mins=5)
        debug_info.append(f'last 5 mins avg price: {last_5mins_avg}')
        last_60mins_avg = self.get_avg_price(quotation, mins=60)
        debug_info.append(f'last 60 mins avg price: {last_60mins_avg}')

        try:
            assert [current_price, last_5mins_avg, last_60mins_avg]
        except AssertionError:
            raise Exception('error when trying to get prices!')

        if self.DEBUG:
            for info in debug_info:
                print(info)

        try:
            # accept ratios when init
            if current_price < last_5mins_avg * 0.995:
                result.update({'现价低于 5 分钟均价' : f'{1 - current_price / last_5mins_avg:.2%}'})
                result.update({'现价': f'{current_price}'})
                result.update({'5 分钟均价': f'{last_5mins_avg:.2f}'})
            # elif current_price < last_60mins_avg * 0.995:
            #    result.update({'现价低于 60 分钟均价' : f'{1 - current_price / last_60mins_avg:.2%}'})
        except Exception:
            raise Exception('catch quick_v failed!')

        return result


async def main():
    while True:
        o = Oscillator(debug=True)
        if o.IS_TRADING:
            await o.do_job()
            time.sleep(20)
        else:
            time.sleep(63000)


if __name__ == "__main__":
    asyncio.run(main())
