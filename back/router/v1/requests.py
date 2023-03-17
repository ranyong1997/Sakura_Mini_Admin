#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/17 11:31
# @Author  : 冉勇
# @Site    : 
# @File    : requests.py
# @Software: PyCharm
# @desc    : 发送接口
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter(
    prefix="/v1",
    tags=["Requests"],
    responses={404: {"description": "Not Found"}}
)


class RequestItem(BaseModel):
    url: str
    method: str
    headers: Dict[str, str] = None
    body: Dict[str, str] = None


@router.post("/send_request/")
async def send_request(request_item: RequestItem) -> Dict[str, Any]:
    url = request_item.url
    method = request_item.method.upper()
    headers = request_item.headers
    body = request_item.body
    # 检查请求方法是否有效
    if method not in ["GET", "POST", "PUT", "DELETE"]:
        raise HTTPException(status_code=400, detail="Invalid request method")
    # 发送请求并接收响应
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=headers, json=body)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    # 检查响应是否成功
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"response": response.json()}
