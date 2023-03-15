#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 11:00
# @Author  : 冉勇
# @Site    : 
# @File    : access_middle.py
# @Software: PyCharm
# @desc    : 记录请求日志
from datetime import datetime
from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from back.utils.logger import log


class AccessMiddleware(BaseHTTPMiddleware):
    """
    记录请求日志
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = datetime.now()
        response = await call_next(request)
        end_time = datetime.now()
        log.info(f"{response.status_code} {request.client.host} {request.method} {request.url} {end_time - start_time}")
        return response
