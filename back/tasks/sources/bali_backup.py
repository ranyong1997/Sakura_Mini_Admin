#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/7 16:59
# @Author  : 冉勇
# @Site    : 
# @File    : bali_backup.py
# @Software: PyCharm
# @desc    :
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess

app = FastAPI()

scheduler = BackgroundScheduler()


# 定义备份任务
async def backup():
    filename = datetime.now().strftime("backup-%Y-%m-%d-%H-%M-%S.sql")
    subprocess.run(["pg_dump", "-U", "username", "-f", filename, "database_name"])


# 定义迁移任务
async def migrate():
    subprocess.run(["alembic", "upgrade", "head"])


# 定义定时任务
scheduler.add_job(func=backup, trigger='cron', hour=2)
scheduler.add_job(func=migrate, trigger='cron', hour=3)
