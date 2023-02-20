#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/20 17:14
# @Author  : 冉勇
# @Site    : 
# @File    : generate_string.py
# @Software: PyCharm
# @desc    : 生成UUID和时间戳
import datetime
import uuid


def get_uuid() -> str:
    """
    生成uuid
    :return: str(uuid)
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> float:
    """
    生成当前时间戳

    :return:
    """
    return datetime.datetime.now().timestamp()
