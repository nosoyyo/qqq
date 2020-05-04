# generating signals and send via bot

import time
import asyncio

from config import Portfolio
from gateway import Gateway


class Oscillator():

    symbols = Portfolio.symbols
    g = Gateway()

    def __init__(self):
        pass

    async def do_job(self):
        while True:
            try:
                for symbol in symbols:
                    quotation = await self.g.hgetall(symbol)
                    last_5mins_price = self.get_avg_price(symbol, 5)
                time.sleep(10)
            except Exception:
                raise Exception('..')
                time.sleep(10)
            finally:
                time.sleep(10)

    def get_avg_price(self, quotation: dict, mins: int=5):
        '''
        :return: 
        '''
        result = None
        keys_list = [float(i) for i in quotation]
        keys_list.sort()
        now = time.time()
        keys = [i for i in keys_list if i > now - (60 * mins)]
        if keys:
            prices = [quotation[str(i)] for i in keys]
            try:
                prices = [float(i) for i in prices]
                result = sum(prices) / len(prices)
            except TypeError:
                raise Exception('data type error!')
        return result


if if __name__ == "__main__":
    o = Oscillator()
    await o.do_job()
