import time
from datetime import datetime


class TradeDay():

    def ymd(self, day=None) -> tuple:
        '''
        temporarily different with <lizhu>'s ymd()
        will change that one, not this one, for this one is newer

        :param day: TODO: a particular day
        '''
        if not day:
            today = datetime.today()
        return today.year, today.month, today.day


    def get_day8(self, day=None) -> str:
        '''
        :return: something like '20200502'
        '''
        if not day:
            day = datetime.today()
        y, m, d = f'{day.year}', f'{day.month:02}', f'{day.day:02}'
        return y+m+d


    def is_trading(self):
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
