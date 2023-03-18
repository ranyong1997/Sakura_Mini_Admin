#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/17 11:31
# @Author  : 冉勇
# @Site    : 
# @File    : requests_router.py
# @Software: PyCharm
# @desc    : 发送接口
import httpx
from typing import Dict, Any
from fastapi import FastAPI, APIRouter, Body, HTTPException
from back.schemas import requests_schemas

router = APIRouter(
    prefix="/v1",
    tags=["Requests"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/send_request/")
async def send_http_request(request_item: requests_schemas.RequestItem) -> Dict[str, Any]:
    """
     发送Http接口
    """
    # 检查请求方法是否有效
    if request_item.method not in ["GET", "POST", "PUT", "DELETE"]:
        raise HTTPException(status_code=400, detail="Invalid request method")
        # 发送请求并接收响应
    async with httpx.AsyncClient() as client:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request_item.method,
                    url=request_item.url,
                    headers=request_item.headers,
                    params=request_item.params,
                    data=request_item.data,
                    json=request_item.JSON,
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=str(e))
    # 检查响应是否成功
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"response": response.json()}
