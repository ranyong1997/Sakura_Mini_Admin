#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:33
# @Author  : 冉勇
# @Site    : 
# @File    : token.py
# @Software: PyCharm
# @desc    : 令牌工具
from datetime import timedelta, datetime
from jose import JWTError, jwt
from pydantic import BaseSettings
from back.app import settings
from fastapi.security import OAuth2PasswordBearer
from back.dbdriver.mysql import get_db
from back.models.db_user_models import User
from fastapi import HTTPException, status
from typing import Union

# 执行生成token的地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.url_prefix)


class AppTokenConfig(BaseSettings):
    """
    在终端通过以下命令生成一个新的密匙:
    >>>openssl rand -hex 32<<<
    ⚠️加密密钥 这个很重要千万不能泄露了，而且一定自己生成并替换。⚠️
    """
    SECRET_KEY = settings.jwt_secret_key
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
        payload = jwt.decode(token, APP_TOKEN_CONFIG.SECRET_KEY, algorithms=[APP_TOKEN_CONFIG.ALGORITHM])
        username: str = payload.get("sub")  # 从 token中获取用户名
        return username
    except JWTError as e:
        raise credentials_exception from e


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    生成token
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 生成带有时间限制的token
    encoded_jwt = jwt.encode(to_encode, APP_TOKEN_CONFIG.SECRET_KEY, algorithm=APP_TOKEN_CONFIG.ALGORITHM)
    return encoded_jwt
