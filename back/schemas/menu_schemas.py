#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/5 10:16
# @Author  : 冉勇
# @Site    : 
# @File    : menu_schemas.py
# @Software: PyCharm
# @desc    :
from typing import Optional

from pydantic import BaseModel


class Menu(BaseModel):
    """
    正常请求，处理返回消息类
        :param code: 返回的状态码
        :param msg: 提示消息
        :param data: 具体数据
    """
    code: int = 200
    msg: str = "成功"
    success: bool = True
    data: Optional[dict] = None

    def __init__(self, data: list = None, msg: str = "成功", code: int = 200, success: bool = True):
        super().__init__()
        self.code = code
        self.data = data
        self.msg = msg
        self.success = success
        if data is None:
            delattr(self, "data")
