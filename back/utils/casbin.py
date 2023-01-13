#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:53
# @Author  : 冉勇
# @Site    : 
# @File    : casbin.py
# @Software: PyCharm
# @desc    : 权限工具
import os
import sys
from fastapi import HTTPException, status
from back.app import settings
from back.app.database import get_casbin
from back.utils.token import get_username_by_token, verify_isActive
from loguru import logger

LOG_LEVEL = settings.LOG_LEVEL
logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
logger.add(os.path.join(settings.BASE_DIR, settings.log_dir), level=LOG_LEVEL)
handler_id = logger.add(sys.stderr, level=LOG_LEVEL)


def verify_enforce(token: str, rule):
    """
    casbin权限验证
    :param token:
    :param rule:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="您的账户已锁定",
        headers={"WWW-Authenticate": "Bearer"}
    )
    e = get_casbin()  # 每次都要调用,获取最新的权限规则
    sub = get_username_by_token(token)  # token中获取用户名
    print("casbin.py # 35 ", sub, rule)
    if not verify_isActive(sub):
        return e.enforce(sub, rule.obj, rule.act)
    else:
        raise credentials_exception
