import random
from datetime import datetime


def is_trading():
    flag = False
    now = datetime.now()
    if now.weekday() > 5:
        return flag
    if now < datetime(2020, 11, 1):
        OVER = datetime(now.year,now.month,now.day,4,0)
        START = datetime(now.year,now.month,now.day,21,30)
    else:
        OVER = datetime(now.year,now.month,now.day,5,0)
        START = datetime(now.year,now.month,now.day,22,30)
    if not OVER < now < START:
        flag = True
    return flag


def get_nearest_ts(time_list: list,
                    ts_given: float,
                    n_ele: int=1,
                    debug=False
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


def small_talk(want):
    prefixes = ['', '那么，', '', '咳咳，', '', '嘿嘿，', '', '啊...', '', '嗯...',
                '我看看，', '', '我看下啊...', '', '嚯！', '', '嗯哼，', '', '嗯呢，',
                '', '哦哦，', '', '哦唷', '', '啧啧，', '', '喔，', '', ]
    suffixes = ['对吧', '', '狸']
    middle = ['的话，', '', ]
    if want == 'prefix':
        result = random.choice(prefixes)
    elif want == 'suffix':
        result = random.choice(suffixes)
    elif want == 'middle':
        result = random.choice(middle)
    return result


def lify(d):
    content = ''
    mid = small_talk('middle')
    for k in d:
        if isinstance(d[k], dict):
            prefix = small_talk('prefix')
            sentence = f'{prefix} **{k}** {mid}...\n'
            content += sentence
            content += lify(d[k])
        else:
            mid = small_talk('middle')
            prefix = small_talk('prefix')
            suffix = small_talk('suffix')
            sentence = f'{prefix}{k}{mid}是** {d[k]} **{suffix}\n'
            content += sentence

    return content


def ill_minded(p):
    result = ''
    k = int(len(p)*random.random())
    if k < 2:
        k = 2
    ill = random.choices(p, k=k)
    for i in ill:
        result += i
    return result


def deaf(msg):
    return f'{small_talk("prefix")}你说{ill_minded(msg)}？听见了狸！'

