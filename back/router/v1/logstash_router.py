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
from back.utils.logging_setup import setup_root_logger


setup_root_logger()

LOGGER = logging.getLogger(__name__)

LOGGER.info("---Starting App---")
router = APIRouter(
    prefix="/v1",
    tags=["ELK"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get("/random_uuid")
async def root():
    LOGGER.info(str(uuid.uuid4()))
    return {"message": "OK"}
