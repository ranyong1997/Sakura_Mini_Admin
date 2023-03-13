#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/9 17:54
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    :
from back.dbdriver.mysql_ import get_database_pool, get_async_database_pool
from back.dbdriver.redis_ import get_redis_connect_pool, get_sync_redis_connect_pool

redis = get_redis_connect_pool()
sync_redis = get_sync_redis_connect_pool()
mysql = get_database_pool()
async_mysql = get_async_database_pool()