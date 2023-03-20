#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/17 11:31
# @Author  : 冉勇
# @Site    : 
# @File    : requests_router.py
# @Software: PyCharm
# @desc    : 发送接口
import aiohttp
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from back.models.db_request_detail import RequestDetail
from back.models.db_requests_log import RequestLog
from back.schemas import requests_schemas
from sqlalchemy.orm import Session
from back.dbdriver.mysql import get_db

router = APIRouter(
    prefix="/v1",
    tags=["Requests"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/send_request/", summary="发送Http接口")
async def send_http_request(request_item: requests_schemas.RequestItem,
                            db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
     发送Http接口
    """
    # 检查请求方法是否有效
    if request_item.method not in ["GET", "POST", "PUT", "DELETE"]:
        raise HTTPException(status_code=400, detail="请求方法无效")
    # 记录请求方法、url、参数、data、json
    log = RequestLog(
        method=request_item.method,
        url=request_item.url,
        headers=request_item.headers,
        params=request_item.params,
        JSON=request_item.JSON
    )
    # todo:封装成方法
    # 将记录插入数据库
    db.add(log)
    db.commit()
    async with aiohttp.ClientSession() as session:
        # 发送请求并接收响应
        try:
            async with session.request(
                    method=request_item.method,
                    url=request_item.url,
                    headers=request_item.headers,
                    params=request_item.params,
                    json=request_item.JSON
            ) as response:
                # 记录请求结果
                detail = RequestDetail(
                    id=log.id,
                    status_code=response.status,
                    text=await response.text(),
                    json=await response.json(encoding="utf-8")
                )
                # todo:封装成方法
                db.add(detail)
                db.commit()
                # 检查响应是否成功
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=await response.text())
                return {"response": await response.json()}
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
