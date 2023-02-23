#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:19
# @Author  : 冉勇
# @Site    : 
# @File    : user_schemas.py
# @Software: PyCharm
# @desc    : 用户模型
from typing import Union, Optional
from pydantic import BaseModel


class Token(BaseModel):
    code: int = 200
    msg: str = 'Success'
    access_token: str
    token_type: str = 'Bearer'
    is_superuser: Optional[bool] = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    username: str
    password: str
    sex: str


class User(UserBase):
    id: int
    username: str
    sex: str
    email: str
    is_active: bool
    avatar: Union[str, None] = None
    remark: Union[str, None] = None

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    user_id: int
    username: str
    password: Union[str, None] = ''
    sex: str
    email: str
    avatar: Union[str, None] = None
    remark: Union[str, None] = None


class Users(BaseModel):
    users: list
    count: int


class ChangeUserRole(BaseModel):
    user_id: int
    names: list


class Casbin_rule(BaseModel):
    obj: str
    act: str
