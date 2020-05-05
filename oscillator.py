# generating signals then send via bot
# TODO: need to fix last_open

import time
import asyncio

from gateway import Gateway
from feishu_bot import FeishuBot
from utils import lify, is_trading
from models import BaseTimePriceModel
from config import Portfolio, FeishuConf


class Oscillator(BaseTimePriceModel):

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
        result = {}

        try:
            for symbol in self.symbols:
                if self.DEBUG:
                    print(f'doing {symbol}')
                quotation = await self.g.hgetall(f'{symbol}_price')
                analysis = self.analyze(quotation)

                # catch instan V shape
                quick_v = self.catch_quick_v(analysis)
                if quick_v:
                    result[symbol] = quick_v

                # catch quick drop
                quick_drop = self.catch_quick_drop(analysis)
                if quick_drop:
                    result[symbol] = quick_drop
                
                # catch below open
                # below_open = self.catch_below_open(analysis)
                # if below_open:
                #     result[symbol] = below_open
                

            if result:
                if self.DEBUG:
                    print(result)
                volume = await self.g.hgetall(f'{symbol}_volume')
                await self.bot.send_text(lify(result), groups=FeishuConf.MSFC)
                
        except Exception:
            raise Exception(f'do_job for {symbol} failed')


    def analyze(self, quotation: dict) -> dict:
        debug_info = []
        result = {}

        try:
            time_list = self._serialize_time(quotation)
        except Exception:
            raise Exception('error getting time_list from quotation!')

        try:
            current_price = self._read_ts_dict(quotation, time.time())
            debug_info.append(f'current price: {current_price}')
        except Exception:
            raise Exception('error getting current_price!')

        try:
            price_1min_ago = self._read_ts_dict(quotation, time.time() - 60)
            debug_info.append(f'price 1min ago: {price_1min_ago}')
        except Exception:
            raise Exception('error getting price_1min_ago!')

        try:
            last_5mins_avg = self._get_avg_price(quotation, mins=5)
            debug_info.append(f'last 5 mins avg price: {last_5mins_avg}')
        except Exception:
            raise Exception('error getting 5 mins avg price!')

        try:
            last_60mins_avg = self._get_avg_price(quotation, mins=60)
            debug_info.append(f'last 60 mins avg price: {last_60mins_avg}')
        except Exception:
            raise Exception('error getting 60 mins avg price!')

        try:
            # TODO need fix _get_last_open
            last_open = self._get_last_open(quotation)
            debug_info.append(f'last trade day open at: {last_open}')
        except Exception:
            raise Exception('error getting last open!')      

        try:
            last_close = self._get_last_close(quotation)
            debug_info.append(f'last trade day close at: {last_close}')
        except Exception:
            raise Exception('error getting last close!')      

        if self.DEBUG:
            for info in debug_info:
                print(info)

        result['current_price'] = current_price
        result['price_1min_ago'] = price_1min_ago
        result['last_5mins_avg'] = last_5mins_avg
        result['last_60mins_avg'] = last_60mins_avg
        result['last_open'] = last_open
        result['last_close'] = last_close

        return result

    def catch_quick_v(self, analysis: dict):
        '''
        for catching instant V shape

        :param analysis: a dict looks like
                         {'current_price' : 123.45,
                          'last_5mins_avg' : 134.56,
                          'last_60mins_avg : 145.67,
                          }

        :return: a descriptive dict to be lified
        '''
        result = {}
        current_price = analysis['current_price']
        last_5mins_avg = analysis['last_5mins_avg']

        try:
            # accept ratios when init
            if current_price < last_5mins_avg * 0.992:
                result.update({'现价低于 5 分钟均价' : f'{1 - current_price / last_5mins_avg:.2%}'})
                result.update({'现价': f'{current_price}'})
                result.update({'5 分钟均价': f'{last_5mins_avg:.2f}'})
            # elif current_price < last_60mins_avg * 0.995:
            #    result.update({'现价低于 60 分钟均价' : f'{1 - current_price / last_60mins_avg:.2%}'})
        except Exception:
            raise Exception('catch quick_v failed!')

        return result

    def catch_below_open(self, analysis: dict):
        '''
        for catching below open stocks

        :param analysis: a dict looks like
                         {'current_price' : 123.45,
                          'last_5mins_avg' : 134.56,
                          'last_60mins_avg : 145.67,
                          }

        :return: a descriptive dict to be lified
        '''
        result = {}
        current_price = analysis['current_price']
        last_open = analysis['last_open']

        try:
            # accept ratios when init
            if current_price < last_open * 0.98:
                result.update({'现价低于今日开盘' : f'{1 - current_price / last_open:.2%}'})
                result.update({'现价': f'{current_price}'})
                result.update({'今日开盘': f'{last_open:.2f}'})
        except Exception:
            raise Exception('catch below_open failed!')

        return result

    def catch_quick_drop(self, analysis: dict):
        '''
        for catching instant drop

        :param analysis: a dict looks like
                         {'current_price' : 123.45,
                          'last_5mins_avg' : 134.56,
                          'last_60mins_avg : 145.67,
                          }

        :return: a descriptive dict to be lified
        '''
        result = {}
        current_price = analysis['current_price']
        price_1min_ago = analysis['price_1min_ago']

        try:
            # accept ratios when init
            if current_price < price_1min_ago * 0.992:
                result.update({'现价低于 1 分钟之前' : f'{1 - current_price / price_1min_ago:.2%}'})
                result.update({'现价': f'{current_price}'})
                result.update({'1 分钟之前': f'{price_1min_ago:.2f}'})
        except Exception:
            raise Exception('catch quick_drop failed!')

        return result

async def main():
    while True:
        try:
            o = Oscillator(debug=True)
            if o.IS_TRADING:
                await o.do_job()
                time.sleep(20)
            else:
                time.sleep(63000)
        except Exception:
            warning = 'Oscillator() 异常退出了狸！'
            await o.bot.send_text(warning, groups=FeishuConf.MSFC)
            raise Exception('unknown exception!')


if __name__ == "__main__":
    asyncio.run(main())
