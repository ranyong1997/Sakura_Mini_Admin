#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/7 17:16
# @Author  : 冉勇
# @Site    : 
# @File    : redis_router.py
# @Software: PyCharm
# @desc    :
import json
from fastapi import APIRouter, Depends
from back.app.database import get_rdb
from back.schemas.redis_schemas import Item
from redis import Redis

# from back.utils.connection import get_rdb

router = APIRouter(
    prefix="/v1",
    tags=["Redis单元测试"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


################################
# role相关的api接口
################################
# @router.post("/item/", response_model=Item)
@router.post("/item/")
async def create_item(rdb: Redis = Depends(get_rdb)):
    # rdb.set('name', '123')
    rdb.set('userinfo:shanghai:zhangsan', 'user')

# @router.get("/item/", response_model=Item)
# async def get_item(rdb: Redis = Depends(init_redis)):
#     obj = rdb.get('item_name')
#     return json.loads(obj)
