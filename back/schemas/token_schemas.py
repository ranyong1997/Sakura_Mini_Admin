#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 11:53
# @Author  : 冉勇
# @Site    : 
# @File    : token_schemas.py
# @Software: PyCharm
# @desc    : token模型
from typing import Union
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

