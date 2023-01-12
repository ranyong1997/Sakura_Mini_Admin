#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:33
# @Author  : 冉勇
# @Site    : 
# @File    : token.py
# @Software: PyCharm
# @desc    : 令牌工具
import os
import sys
from jose import JWTError, jwt
from loguru import logger
from pydantic import BaseSettings
from back.app import settings
from fastapi.security import OAuth2PasswordBearer
from back.app.database import BASE_DIR, get_db
from back.models.db_user_models import User
from fastapi import HTTPException, status

LOG_LEVEL = settings.LOG_LEVEL  # 日志等级
logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
logger.add(os.path.join(BASE_DIR, settings.log_dir), level=LOG_LEVEL)
handler_id = logger.add(sys.stderr, level=LOG_LEVEL)

# 执行生成token的地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.url_prefix)


class AppTokenConfig(BaseSettings):
    """
    在终端通过以下命令生成一个新的密匙:
    >>>openssl rand -hex 32<<<
    ⚠️加密密钥 这个很重要千万不能泄露了，而且一定自己生成并替换。⚠️
    """
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_exp_seconds  # token失效时间


# 创建一个token配置项
APP_TOKEN_CONFIG = AppTokenConfig()


def verify_isActive(username: str):
    """
    判断用户是否锁定
    :param username: 用户名
    :return: boolean
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="当前用户不存在或已被删除",
        headers={"WWW-Authenticate": "Bearer"}
    )
    user = next(get_db()).query(User).filter_by(username=username).first()
    if user:
        return user.is_active
    else:
        raise credentials_exception


def get_username_by_token(token):
    """
    从token中取出username
    :param token:
    :return: username
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        print("token.py # 56 获取用户名" + token)
        payload = jwt.decode(token, APP_TOEKN_CONFIG.SECRET_KEY, algorithms=[APP_TOEKN_CONFIG.ALGORITHM])
        username: str = payload.get('sub')  # 从token中获取用户名
        return username
    except JWTError:
        raise credentials_exception


def verify_e(e, sub, obj, act):
    """

    :param e:
    :param sub:
    :param obj:
    :param act:
    :return:
    """
    return e.enforce(sub, obj, act)