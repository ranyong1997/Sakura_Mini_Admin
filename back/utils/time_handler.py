#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/9 14:46
# @Author  : 冉勇
# @Site    : 
# @File    : time_handler.py
# @Software: PyCharm
# @desc    : 一些日期相关的工具
from datetime import datetime, date, timedelta


def time_remaining(type_: str = "Day") -> int:
    """
    获取距离指定时间剩余时间
    :param type_: 类型
        Day: 今天剩余时间
        Week:本周剩余时间
        Month:本月剩余时间
        Year: 本年剩余时间
    :return: 剩余时间的秒数
    """
    type_ = type_.lower()
    now = datetime.now()
    today = datetime.strptime(str(date.today()), "%Y-%m-%d")
    if type_ == "week":
        expecte_time = today - timedelta(days=today.weekday()) + timedelta(days=7)
    elif type_ == "month":
        next_month = today.replace(day=28) + timedelta(days=4)
        expecte_time = next_month - timedelta(days=next_month.day - 1)
    elif type_ == "year":
        expecte_time = datetime(today.year + 1, 1, 1)
    else:
        expecte_time = today + timedelta(days=1)
    time_diff = expecte_time - now
    return time_diff.days * 24 * 3600 + time_diff.seconds


def rest_of_day():
    """
    截止到目前当前时间剩余时间
    :return: 剩余时间的秒数
    """
    today = datetime.strptime(str(date.today()), "%Y-%m-%d")
    tomorrow = today + timedelta(days=1)
    nowTime = datetime.now()
    seconds = (tomorrow - nowTime).seconds
    if seconds < 5:
        seconds = 5
    return seconds  # 获取秒


def rest_of_next_half_hour(format="default"):
    """
    获取当前时间到下一个半小时的剩余时间
    :param format:
    :return: 返回剩余的时间戳;strf返回下一次执行的时间
    """
    now = datetime.now()
    now_minute = now.minute
    now_second = now.second
    if now_minute < 30:
        dif_minute = 30 - now_minute
    else:
        dif_minute = 60 - now_minute
    next_time = now + timedelta(minutes=dif_minute, seconds=-now_second)
    if format == 'default':
        return dif_minute * 60 - now_second
    else:
        return next_time.strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp(date_time: str = None, days: int = 0, hours: int = 0, minutes: int = 0):
    """
    获取某一时间的时间戳
    :param date_time:
    :param days:
    :param hours:
    :param minutes:
    :return: %Y-%m-%d %H:%M:%S
    """
    if date_time:
        ti = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    else:
        ti = datetime.now()
    the_time = ti + timedelta(days=days, hours=hours, minutes=minutes)
    return int(the_time.timestamp())


def get_last_week_start(date=datetime.now()):
    """
    获取上周的周一
    :param date:
    :return:
    """
    last_week_start = date - timedelta(days=date.weekday() + 7)
    return last_week_start.strftime("%Y%m%d")


def target_monday(today, format="%Y%m%d"):
    """
    :param today: 指定的日期字符串
    :param format: 日期的字符串格式,用于转为datetime
    :return: 返回周一的日期字符串,格式"%Y%m%d"
    """
    today = datetime.strptime(today, format)
    return datetime.strftime(today - timedelta(today.weekday()), "%Y%m%d")


if __name__ == '__main__':
    print(f"距离今天00:00还剩{time_remaining(type_='Day')}秒")
    print(f"距离周日还剩{time_remaining(type_='Week')}秒")
    print(f"距离本月结束还剩{time_remaining(type_='Month')}秒")
    print(f"距离本年结束还剩{time_remaining(type_='Year')}秒")
    print(rest_of_day())
    print(rest_of_next_half_hour())
    print(get_timestamp())
    print(get_last_week_start())
    print(target_monday())
