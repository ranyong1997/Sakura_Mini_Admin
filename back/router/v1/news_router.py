#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/19 11:07
# @Author  : 冉勇
# @Site    : 
# @File    : news_router.py
# @Software: PyCharm
# @desc    : 60秒读世界路由
from fastapi import APIRouter, Response
from back.utils.crawler import main as new

router = APIRouter(
    prefix="/v1",
    tags=["每日60秒读世界"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get("/news_api")
def news(response: Response, index: int = 0, origin: str = 'zhihu', cache: str = 'null'):
    response.headers["Cache-Control"] = "max-age=86400, immutable, stale-while-revalidate"
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Access-Control-Allow-Origin"] = "*"
    if origin == "undefined":
        origin = "zhihu"
    return new(index, origin)
