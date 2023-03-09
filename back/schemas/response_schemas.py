#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/9 16:13
# @Author  : 冉勇
# @Site    : 
# @File    : response_schemas.py
# @Software: PyCharm
# @desc    :
from typing import Optional, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from back.utils.exception.errors import SYSTEM_ERROR


class Response(BaseModel):
    """
    正常请求，处理返回消息类
        :param code: 返回的状态码
        :param msg: 提示消息
        :param data: 具体数据
    """
    code: int = 200
    msg: str = "OK"
    success: bool = True
    data: Optional[dict] = None

    def __init__(self, data: Any = None, msg: str = "OK", code: int = 200, success: bool = True):
        super().__init__()
        self.code = code
        self.data = data
        self.msg = msg
        self.success = success
        if data is None:
            delattr(self, "data")


class HttpException(Exception):
    def __init__(self, code: int = 400, msg: str = "", error_code: int = SYSTEM_ERROR, error: str = "",
                 body: dict = {}):
        """
        请求抛出异常，处理返回消息类
            :param code: 返回的状态码
            :param msg: 错误提示消息
            :param error: 系统报错信息
            :param error_code: 内部错误码，详情见setting.error_code文件
        """
        self.code = code
        self.message = msg
        self.error_code = error_code
        self.error = error
        self.body = body


class ErrorResponse(JSONResponse):
    """
    错误消息的想要
        :param code: 返回的状态码
        :param msg: 提示消息
        :param error_code: 错误码
    """

    def __init__(self,
                 code: int = 500,
                 msg: str = "内部错误！",
                 error_code: Optional[int] = None):
        super().__init__(status_code=code,
                         content={
                             "message": msg,
                             "error_code": error_code
                         })
