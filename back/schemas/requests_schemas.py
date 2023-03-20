#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 11:12
# @Author  : 冉勇
# @Site    : 
# @File    : requests_schemas.py
# @Software: PyCharm
# @desc    :
from pydantic import BaseModel


class RequestItem(BaseModel):
    url: str
    method: str
    headers: dict
    params: dict
    JSON: dict
