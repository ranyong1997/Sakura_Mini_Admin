#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:50
# @Author  : 冉勇
# @Site    : 
# @File    : password.py
# @Software: PyCharm
# @desc    : 密码加密、解密工具
from passlib.context import CryptContext

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


def verity_password(plain_password: str, hashed_password: str) -> bool:
    """
    密码校验

    :param plain_password: 要验证的密码
    :param hashed_password: 要比较的hash密码
    :return: 比较密码之后的结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    hash密码
    :param password: 未加密密码
    :return: 哈希加密密码
    """
    return pwd_context.hash(password)
