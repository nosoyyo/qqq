import time
from datetime import datetime

from .tradeday import TradeDay


class BaseTimePriceModel(TradeDay):


    def __init__(self, debug=False):
        '''
        this model deals with a format looks like
        {
            '1588702002.603742' : 143.08
        }
        '''
        self.IS_TRADING = self.is_trading()
        self.DEBUG = False
        if debug:
            self.DEBUG = True
            

    def _read_ts_dict(self,
                      _dict,
                      ts,
                      ):
        '''
        for reading a particular dict format looks like
        {timestamp : float}
        e.g. {1588620813.466 : 3243562}

        :return: normally a `float`, or an `int`
        '''
        result = None

        try:
            result = float(_dict[str(ts)])
        except KeyError:
            debug_info = f'no timestamp give, will look for nearest ts for'
            if self.DEBUG:
                print(f'{debug_info} {ts}')
            time_list = self._serialize_time(_dict)
            key = self._get_nearest_ts(time_list, ts, n_ele=1)
            if isinstance(key, list):
                key = key[0]
            result = float(_dict[str(key)])
        return result

    def _serialize_time(self, quotation: dict) -> list:
        result = [float(i) for i in quotation]
        result.sort()
        return result

    def _get_avg_price(self, quotation: dict, mins: int=5) -> float:
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
        return float(result)

    def _get_nearest_ts(
                        self,
                        time_list: list,
                        ts_given: float,
                        n_ele: int=1,
                        debug=False,
                        ):
        '''
        for reading a particular dict format looks like
        {timestamp : float}
        e.g. {1588620813.466 : 3243562}


        :param n_ele: num of elements you want to strip out
        :return: float if not backward
        :return: list if backward, with n of nearest elements
        '''
        time_list.sort()
        result = []

        try:
            if not n_ele:
                raise ZeroDivisionError('num of elements cannnot be zero!')
            elif not isinstance(n_ele, int):
                raise TypeError('num of elements must be `int`!')
            elif -2 < n_ele < 1:
                raise Exception('invalid n_ele')

            if abs(n_ele) >= len(time_list):
                result = time_list
            elif ts_given > time_list[-1]:
                result = time_list[-abs(n_ele):]
            elif ts_given < time_list[0]:
                result = time_list[:abs(n_ele)]
            else:
                d = 0
                for t in time_list:
                    if not d:
                        d = ts_given - t
                    if abs(ts_given - t) < d:
                        d = ts_given - t
                        result = t
                        if debug:
                            print(f'result in loop: {result}')

                if n_ele < 0:
                    end = time_list.index(result) + 1
                    begin = end + n_ele
                    if begin <= 0:
                        begin = 0
                    result = time_list[begin:end]
                    if debug:
                        print(f'n_ele < 0: {begin} | {end} | {result}')
                else:
                    begin = time_list.index(result)
                    end = begin + n_ele
                    result = time_list[begin:end]
                    if debug:
                        print(f'n_ele > 0 time_list[{begin}:{end}]')
        except Exception as e:
            print(e)
        return result

    def _get_last_open(self, quotation: dict) -> float:
        y, m, d = self.ymd()
        h = datetime.today().hour
        ts = datetime(y, m, d, 21, 30).timestamp()
        if self.IS_TRADING and h < 4:
            ts = ts - 86400
        elif not self.IS_TRADING:
            ts = ts - 86400
        return self._read_ts_dict(quotation, ts)

    def _get_last_close(self, quotation: dict) -> float:
        y, m, d = self.ymd()
        h = datetime.today().hour
        ts = datetime(y, m, d, 4, 00).timestamp()
        if self.IS_TRADING and h < 4:
            ts = ts - 86400
        return self._read_ts_dict(quotation, ts)

