#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 16:17
# @Author  : 冉勇
# @Site    : 
# @File    : logger.py
# @Software: PyCharm
# @desc    : 日志封装
import inspect
import os
from loguru import logger

from back.app import settings


class Log(object):
    def __init__(self):
        if not os.path.exists(settings.log_dir2):
            os.mkdir(settings.log_dir2)

    def info(self, msg: str):
        """
        普通日志
        :param self:
        :param msg:
        :return:
        """
        pass

    def error(self, msg: str):
        """
        错误日志
        :param msg:
        :return:
        """
        pass

    def warning(self, msg: str):
        """
        警告日志
        :param msg:
        :return:
        """
        pass

    def debug(self, msg: str):
        """
        DEBUG日志
        :param msg:
        :return:
        """
        pass
