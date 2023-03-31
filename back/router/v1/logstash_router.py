#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 17:13
# @Author  : 冉勇
# @Site    : 
# @File    : logstash_router.py
# @Software: PyCharm
# @desc    :
import logging
from fastapi import APIRouter
from logstash_async.handler import AsynchronousLogstashHandler

router = APIRouter(
    prefix="/v1",
    tags=["ELK"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

# 在logstash中配置
"""
input {
  tcp {
    port => 5000
    codec => "json"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "fastapi-%{+YYYY.MM.dd}"
  }
}
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = AsynchronousLogstashHandler(host="localhost", port=5000, database_path="")
logger.addHandler(handler)


@router.get("/")
async def root():
    logger.info("Hello")
    return {"message": "Hello"}
