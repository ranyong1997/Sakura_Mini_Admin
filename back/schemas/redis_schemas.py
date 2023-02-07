#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/6 15:51
# @Author  : 冉勇
# @Site    : 
# @File    : redis_schemas.py
# @Software: PyCharm
# @desc    : redis模型
from pydantic import validator, BaseModel
from back.schemas.base_schemas import SakuraModel


class RedisConfigForm(BaseModel):
    id: int = None
    name: str
    addr: str
    db: int = 0
    password: str = ''
    cluster: bool = False
    env: int

    @validator("name", "addr", "cluster", "db", "env")
    def data_not_empty(cls, v):
        return SakuraModel.not_empty(v)
