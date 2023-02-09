#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/9 14:15
# @Author  : 冉勇
# @Site    :
# @File    : redis.py
# @Software: PyCharm
# @desc    : Redis操作工具类
import sys
from aioredis import Redis, TimeoutError, AuthenticationError
from loguru import logger as log
from back.app.config import Config


class RedisCli(Redis):

    def __init__(self):
        super(RedisCli, self).__init__(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            db=Config.REDIS_DB,
            socket_timeout=Config.REDIS_TIMEOUT,
            decode_responses=True  # 转码 utf-8
        )

    async def init_redis_connect(self):
        """
        触发初始化连接
        :return:
        """
        try:
            await self.ping()
            log.success("连接redis成功")
        except TimeoutError:
            log.error("连接redis超时")
            sys.exit()
        except AuthenticationError:
            log.error("连接redis认证失败")
            sys.exit()
        except Exception as e:
            log.error('连接redis异常 {}', e)
            sys.exit()


# 创建redis连接对象
redis_client = RedisCli()
