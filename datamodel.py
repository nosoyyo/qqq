import time


class BaseDictFormat():
    
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
                print(f'{debug_info} {time.ctime()}')
            time_list = self._serialize_time(_dict)
            key = self._get_nearest_ts(time_list, time.time(), n_ele=1)
            if isinstance(key, list):
                key = key[0]
            result = float(_dict[str(key)])
        return result

    def _serialize_time(self, quotation: dict) -> list:
        result = [float(i) for i in quotation]
        result.sort()
        return result

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
