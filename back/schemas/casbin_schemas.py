#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:24
# @Author  : 冉勇
# @Site    : 
# @File    : casbin_schemas.py
# @Software: PyCharm
# @desc    : 权限模型
from pydantic import BaseModel


class createCasbinObject(BaseModel):
    name: str
    object_key: str
    description: str
    user_id: ine


class EditCasbinObject(BaseModel):
    old_co_id: int
    name: str
    object_key: str
    description: str


class createCasbinAction(BaseModel):
    name: str
    action_key: str
    description: str
    user_id: int


class EditCasbinAction(BaseModel):
    old_ca_id: int
    name: str
    action_key: str
    description: str
