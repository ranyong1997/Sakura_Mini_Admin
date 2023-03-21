#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 09:07
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    :
from fastapi import APIRouter
from back.router.v1 import casbin_router, casbin_action_router, casbin_object_router, role_router, token_router, \
    user_router, fakerdata_router, httprunner_router, news_router, captcha_router, tasks_router, requests_router, \
    pagequery_router, inmail_router

api_v1_router = APIRouter()

# 挂载路由
api_v1_router.include_router(casbin_object_router.router)
api_v1_router.include_router(casbin_router.router)
api_v1_router.include_router(casbin_action_router.router)
api_v1_router.include_router(role_router.router)
api_v1_router.include_router(token_router.router)
api_v1_router.include_router(user_router.router)
api_v1_router.include_router(fakerdata_router.router)
api_v1_router.include_router(httprunner_router.router)
api_v1_router.include_router(news_router.router)
api_v1_router.include_router(captcha_router.router)
api_v1_router.include_router(tasks_router.router)
api_v1_router.include_router(requests_router.router)
api_v1_router.include_router(pagequery_router.router)
api_v1_router.include_router(inmail_router.router)

# swagger标签
tags_metadata = [
    {
        "name": "Casbin权限验证",
        "description": "",
    },
    {
        "name": "Casbin资源",
        "description": "",
    },
    {
        "name": "Casbin行为",
        "description": "",
    },
    {
        "name": "角色",
        "description": "角色相关操作，增删改查",
    },
    {
        "name": "系统登录",
        "description": "获取token",
    },
    {
        "name": "用户",
        "description": "用户相关操作，增删改查",
    },
    {
        "name": "虚拟数据生成器",
        "description": "生成虚拟数据API",
    },
    {
        "name": "HttpRunner",
        "description": "HttpRunner接口测试",
    },
    {
        "name": "每日60秒读世界",
        "description": "60秒读世界API",
    },
    {
        "name": "验证码",
        "description": "验证码API",
    },
    {
        "name": "Requests",
        "description": "发送接口",
    },
    {
        "name": "分页查询演示接口",
        "description": "分页查询演示接口",
    },
]
