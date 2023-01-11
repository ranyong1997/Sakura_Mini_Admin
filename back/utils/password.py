#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:50
# @Author  : 冉勇
# @Site    : 
# @File    : password.py
# @Software: PyCharm
# @desc    : 密码加密、解密工具
import os
import sys
from passlib.context import CryptContext
from loguru import logger
from back.app import settings
from back.main import BASE_DIR

LOG_LEVEL = settings.LOG_LEVEL
logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
logger.add(os.path.join(BASE_DIR, settings.log_dir), level=LOG_LEVEL)
handler_id = logger.add(sys.stderr, level=LOG_LEVEL)

# 密码散列 pwd_context_hash(password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    校验密码
    :param plain_password: 原始密码
    :param hashed_password: 哈希加密密码
    :return: Boolean
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    hash密码
    :param password: 未加密密码
    :return: 哈希加密密码
    """
    return pwd_context.hash(password)
