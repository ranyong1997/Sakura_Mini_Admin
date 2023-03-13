#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:49
# @Author  : 冉勇
# @Site    : 
# @File    : redis_config.py
# @Software: PyCharm
# @desc    : 业务的Redis配置【测试环境】
from back.app.config import Config

redis_1 = {
    "host": Config.REDIS_HOST,
    "port": Config.REDIS_PORT,
    "db": 1,
    "password": Config.REDIS_PASSWORD,
    "timeout": 3600
}

# 业务redis的映射
Redis_Config = {
    '11': redis_1,
}
