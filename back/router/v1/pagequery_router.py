#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 14:35
# @Author  : 冉勇
# @Site    : 
# @File    : pagequery_router.py
# @Software: PyCharm
# @desc    : 分页查询演示接口
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from back.dbdriver.mysql import get_db
from back.models.db_user_models import User
from back.utils.common import paginate

router = APIRouter(
    prefix="/v1",
    tags=["分页查询演示接口"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get("/items/", summary="分页查询演示接口")
def read_items(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    items = paginate(db, User, page, page_size)
    return items
