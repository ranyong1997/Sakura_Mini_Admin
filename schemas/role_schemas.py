#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:23
# @Author  : 冉勇
# @Site    : 
# @File    : role_schemas.py
# @Software: PyCharm
# @desc    : 角色模型
from pydantic import BaseModel


class Role(BaseModel):
    name: str
    role_key: str
    description: str
    user_id: str


class EditRole(BaseModel):
    old_role_id: int
    name: str
    role_key: str
    description: srt


class ChangeRole(BaseModel):
    role_id: int
    checkeds: list


