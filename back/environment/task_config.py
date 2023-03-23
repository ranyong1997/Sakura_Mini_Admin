#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:15
# @Author  : 冉勇
# @Site    : 
# @File    : task_config.py
# @Software: PyCharm
# @desc    : 设置固定的定时任务【可用于测试】
from datetime import datetime, timedelta

source_task = [
    {
        # 获取新的书
        'id': 'new_book',
        # 函数相当对于项目所在的位置
        'func': 'back.tasks.sources.new_book:start_book',
        'args': '',
        'kwargs': {},
        'trigger': 'interval',
        'jobstore': 'source_task',
        'days': 1,  # 间隔时间为 一天
        # 'start_date': datetime.now() + timedelta(minutes=20),  # 开始执行的时间
        'start_date': datetime.now() + timedelta(seconds=10),
        # 'next_run_time': datetime.now(),
        # 'hours': 1,
        # 'minutes': 1,
        # 'seconds': 30,
        'replace_existing': True
    }
]

JOBS = source_task
