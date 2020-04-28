# this thing reaches out to quotation sources

import time
import httpx
from functools import reduce

from config import Portfolio, QQQuotation


class Snapper():

    client = httpx.AsyncClient()
    url = 'http://qt.gtimg.cn/?q='
    
    # for debugging
    _symbol = 'aapl'
    _symbols = ['aapl', 'tvix']

    def __init__(self, s):
        self.client.headers.update(QQQuotation.headers)
        self.s = self._cleansing(s)

    def _cleansing(self, s) -> list:
        '''
        take snapshot for this minute
        :s: one symbol or several symbols
        '''
        symbols = []
        try:
            if isinstance(s, str):
                symbols = [s.upper()]
            elif isinstance(s, list):
                assert all([isinstance(i, str) for i in s])
                assert all([i.isalpha() for i in s])
                symbols = [i.upper() for i in s]
        except Exception:
            raise Exception('param:s: failed in QQQuotation.snap()')
        return symbols

    async def snap(self, s:list=None) -> list:
        result = {}
        if not s:
            s = self.s
        s = [f's_us{i},' for i in s]
        s = reduce(lambda x,y:x+y, s) 

        url = f'{self.url}{s}'
        resp = await self.client.get(url)
        result = self._parse(resp)
        self.result = result
        return result

    def _parse(self, resp) -> dict:
        quotes = resp.text.strip().split(";")
        result = {}
        for quote in quotes:
            info = quote.split("~")
            if len(quote) <= 7:
                continue
            symbol = info[2].split('.')[0]
            result[symbol] = {
                'chn_name': info[1],
                'current_price': info[3],
                'net_change': info[4],
                'amp_change': info[5],
                'volume': info[6],
                'amount': info[7]
            }
        return result

class EndSnapper(Snapper):

    url = 'http://web.ifzq.gtimg.cn/appstock/app/UsMinute/query?code='
    symbols = Portfolio.symbols
    symbols.remove('IXIC')
    symbols.remove('INX')

    def __init__(self):
        self.client.headers['host'] = 'web.ifzq.gtimg.cn'

    async def snap(self) -> dict:
        result = {}
        for symbol in self.symbols:
            try:
                print(f'{time.ctime() } snapping {symbol}...', end='')
                url = f'{self.url}us{symbol}.OQ'
                resp = await self.client.get(url)
                data = resp.json()['data'][f'us{symbol}.OQ']['data']
                result[symbol] = data
                print('Done.')
            except Exception:
                raise Exception(f'failed when snapping {symbol}')
            finally:
                time.sleep(1)
        return result
