#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 09:07
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    :
from pydantic import BaseSettings
import os
from fastapi import APIRouter
from back.router.v1 import casbin_router, casbin_action_router, casbin_object_router, role_router, token_router, \
    user_token, fakerdata_router, httprunner_router

api_v1_router = APIRouter()

# 挂载路由
api_v1_router.include_router(casbin_object_router.router)
api_v1_router.include_router(casbin_router.router)
api_v1_router.include_router(casbin_action_router.router)
api_v1_router.include_router(role_router.router)
api_v1_router.include_router(token_router.router)
api_v1_router.include_router(user_token.router)
api_v1_router.include_router(fakerdata_router.router)
api_v1_router.include_router(httprunner_router.router)
