#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 15:02
# @Author  : 冉勇
# @Site    : 
# @File    : inmail_router.py
# @Software: PyCharm
# @desc    : 站内信
from fastapi import WebSocket, APIRouter

router = APIRouter(
    prefix="/v1",
    tags=["站内信"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
