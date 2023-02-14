#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 14:42
# @Author  : 冉勇
# @Site    : 
# @File    : sys_router.py
# @Software: PyCharm
# @desc    : 任务调度路由
from datetime import datetime
from fastapi import APIRouter, Query, Body
from common.sys_schedule import schedule
from schema.response import response_code
from utils.cron_task import demo_task
