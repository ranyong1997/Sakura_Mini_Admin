#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:39
# @Author  : 冉勇
# @Site    : 
# @File    : redis_.py
# @Software: PyCharm
# @desc    : 异步redis
import redis
from aioredis import Connection, BlockingConnectionPool, Redis
from back import environment
from back.utils.logger import log


class AioRedis:
    """
    异步redis
    """

    def __init__(self, **kwargs):
        self.pool = None
        self.connect_config = dict()
        self.connect_config["host"] = kwargs.get("host")
        self.connect_config["port"] = kwargs.get("port")
        self.connect_config["db"] = kwargs.get("db")
        password = kwargs.get("password")
        if password:
            self.connect_config["password"] = password
        self.expired = kwargs.get("expired")

    async def redis_connect_pool(self):
        """创建连接池"""
        log.info(f"连接Redis: {self.connect_config}")
        self.pool = BlockingConnectionPool(
            max_connections=10,
            timeout=10,
            connection_class=Connection,
            **self.connect_config,
            decode_responses=True
        )

    @property
    def con(self):
        """
        获取redis 原始链接
        :return:
        """
        # 获取到的链接会自动释放回到 pool中
        redis_ob = Redis(connection_pool=self.pool)

        return redis_ob

    async def close(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.disconnect()


class RedisConnection:
    """
    同步redis
    """

    def __init__(self, **kwargs):
        self.pool = None
        self.connect_config = dict()
        self.connect_config["host"] = kwargs.get("host")
        self.connect_config["port"] = kwargs.get("port")
        self.connect_config["db"] = kwargs.get("db")
        password = kwargs.get("password")
        if password:
            self.connect_config["password"] = password
        self.expired = kwargs.get("expired")

    def redis_connect_pool(self):
        log.info(f"连接Sync_Redis: {self.connect_config}")
        self.pool = redis.ConnectionPool(**self.connect_config,
                                         max_connections=8,
                                         decode_responses=True)

    @property
    def con(self):
        """
        获取Redis数据库连接对象
        :return:
        """
        return redis.Redis(connection_pool=self.pool)

    def close(self):
        if self.pool:
            self.pool.disconnect()


def get_redis_connect_pool() -> dict:
    """
    redis链接池创建
    :return:
    {
        "key1": redis_Aioredis_instance,
        "key2": redis_Aioredis_instance,
    }
    """
    redis_pool = dict()
    for redis_db, it in environment.Redis_Config.items():
        aioRedis = AioRedis(**it)
        redis_pool.setdefault(redis_db, aioRedis)
    return redis_pool


def get_sync_redis_connect_pool() -> dict:
    """
    redis链接池创建
    :return:
    {
        "key1": redis_Aioredis_instance,
        "key2": redis_Aioredis_instance,
    }
    """
    redis_pool = dict()
    for redis_db, it in environment.Redis_Config.items():
        aioRedis = RedisConnection(**it)
        redis_pool.setdefault(redis_db, aioRedis)
    return redis_pool
