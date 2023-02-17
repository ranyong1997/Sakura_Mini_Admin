#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 10:23
# @Author  : 冉勇
# @Site    : 
# @File    : httprunner_schemas.py
# @Software: PyCharm
# @desc    :
from pydantic import BaseModel


class HttpRunner_rule(BaseModel):
    case_path: str
    caseId: int
