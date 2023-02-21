#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 10:23
# @Author  : 冉勇
# @Site    : 
# @File    : response_code.py
# @Software: PyCharm
# @desc    : 统一响应状态码(暂废除)
from typing import Union
from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder


def resp_200(data: Union[list, dict, str] = None, message: str = "Success") -> Response:
    """
    请求成功
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            'code': 200,
            'message': message,
            'data': data
        })
    )


def resp_500(data: Union[list, dict, str] = None, message: str = "Internal Server Error") -> Response:
    """
    内部服务器错误
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            'code': 500,
            'message': message,
            'data': data
        })
    )


def resp_4001(data: Union[list, dict, str] = None,
              message: Union[list, dict, str] = "Request Validation Error") -> Response:
    """
    请求验证错误
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            'code': 4001,
            'message': message,
            'data': data
        })
    )


def resp_4002(data: Union[list, dict, str] = None, message: str = "Request Fail") -> Response:
    """
    用户token过期
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            'code': 4002,
            'message': message,
            'data': data
        })
    )


def resp_4003(data: Union[list, dict, str] = None, message: str = "Request Fail") -> Response:
    """
    token认证失败
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            'code': 4003,
            'message': message,
            'data': data
        })
    )


def resp_5002(data: Union[list, dict, str] = None,
              message: Union[list, dict, str] = "Request Fail") -> Response:
    """
    内部验证数据错误
    :param data:
    :param message:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            'code': 5002,
            'message': message,
            'data': data
        })
    )
