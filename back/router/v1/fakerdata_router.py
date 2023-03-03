#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 10:20
# @Author  : 冉勇
# @Site    : 
# @File    : fakerdata_router.py
# @Software: PyCharm
# @desc    : 虚拟数据路由
from fastapi import APIRouter
from back.crud.fakerdata_services import test_data
from back.utils import response_code
from back.utils.logger import log
from back.schemas.fakedata_schemas import FakeData

router = APIRouter(
    prefix="/v1",
    tags=["虚拟数据生成器"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


################################
# 虚拟数据api接口
################################
@router.post('/test/data', summary="获取随机数据")
async def random_data(param: FakeData):
    """
    获取随机数据
    """
    log.info(f"->/test/data的入参信息为---->{param.value}")
    if param.value == "social":
        obj_info = test_data.social_data()
    elif param.value == "organization":
        obj_info = test_data.organization_data()
    else:
        obj_info = test_data.faker_data(param.value)
    return response_code.resp_200(data=obj_info)
