#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/6 11:14
# @Author  : 冉勇
# @Site    : 
# @File    : task.py
# @Software: PyCharm
# @desc    : apscheduler封装
import tzlocal
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from back.app import settings
from back.app.config import Config


class Scheduler:
    @staticmethod
    def _scheduler_conf() -> dict:
        """
        任务配置
        :return:
        """
        redis_conf = {
            'host': Config.APS_REDIS_HOST,
            'port': Config.APS_REDIS_PORT,
            'password': Config.APS_REDIS_PASSWORD,
            'db': Config.APS_REDIS_DATABASE,
            'socket_timeout': Config.APS_REDIS_TIMEOUT
        }
        if settings.APS_TP and settings.APS_PP:
            executor = {
                'default': ThreadPoolExecutor(settings.APS_TP_EXECUTOR_NUM),
                'processpool': ProcessPoolExecutor(settings.APS_PP_EXECUTOR_NUM)
            }
        else:
            executor = None
        end_conf = {
            # 配置存储器
            "jobstores": {
                'default': RedisJobStore(**redis_conf)
            },
            # 配置执行器
            "executors": executor if executor else None,
            # 创建task时默认参数
            "job_defaults": {
                'coalesce': settings.APS_COALESCE,
                'max_instances': settings.APS_MAX_INSTANCES,
            },
            "timezone": str(tzlocal.get_localzone())
        }
        return end_conf

    @property
    def init(self):
        """
        初始化
        :return:
        """
        return BackgroundScheduler(**self._scheduler_conf())

    def start(self, *args, **kwargs):
        """
        开始
        :param args:
        :param kwargs:
        :return:
        """
        self.init.start(*args, **kwargs)

    def shutdown(self, *args, **kwargs):
        """
        结束
        :param args:
        :param kwargs:
        :return:
        """
        self.init.shutdown(*args, **kwargs)


# 调度器
scheduler = Scheduler()
