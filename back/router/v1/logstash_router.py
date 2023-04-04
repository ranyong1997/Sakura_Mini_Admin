#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 17:13
# @Author  : 冉勇
# @Site    : 
# @File    : logstash_router.py
# @Software: PyCharm
# @desc    :
import logging
import uuid
from fastapi import APIRouter

from back.utils.logger import log
# from back.utils.logging_setup import setup_root_logger

# setup_root_logger()

# LOGGER = log.getLogger(__name__)

router = APIRouter(
    prefix="/v1",
    tags=["ELK"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get("/random_uuid")
async def root():
    log.info(str(uuid.uuid4()))
    return {"message": "OK"}
