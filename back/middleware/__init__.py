#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 11:00
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    :
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from back.app import settings
from back.middleware.access_middle import AccessMiddleware


def register_middleware(app: FastAPI) -> None:
    """跨域"""
    if settings.MIDDLEWARE_GZIP:
        app.add_middleware(CORSMiddleware,
                           allow_origins=settings.cors_allow_origins,
                           allow_credentials=True,
                           allow_methods=settings.cors_allow_methods,
                           allow_headers=settings.cors_allow_headers,
                           )
    # gzip
    if settings.MIDDLEWARE_GZIP:
        app.add_middleware(GZipMiddleware)
    # 记录请求日志
    if settings.MIDDLEWARE_ACCESS:
        app.add_middleware(AccessMiddleware)
