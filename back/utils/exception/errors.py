#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/21 17:19
# @Author  : 冉勇
# @Site    : 
# @File    : errors.py
# @Software: PyCharm
# @desc    : 错误状态码
from typing import Any
from fastapi import HTTPException
from back.utils.response.response_code import CodeEnum


class BaseExceptionMixin(Exception):
    code: int

    def __init__(self, *, msg: str = None, data: Any = None):
        self.msg = msg
        self.data = data


class HTTPError(HTTPException):
    pass


class RequestError(BaseExceptionMixin):
    """
    请求错误
    """
    code = 400

    def __init__(self, *, msg: str = '错误代码:400 Bad Request', data: Any = None):
        super().__init__(msg=msg, data=data)


class ForbiddenError(BaseExceptionMixin):
    code = 403

    def __init__(self, *, msg: str = '错误代码:403 Forbidden', data: Any = None):
        super().__init__(msg=msg, data=data)


class NotFoundError(BaseExceptionMixin):
    code = 404

    def __init__(self, *, msg: str = '错误代码:404 Not Found', data: Any = None):
        super().__init__(msg=msg, data=data)


class ServerError(BaseExceptionMixin):
    """
    服务器错误
    """
    code = 500

    def __init__(self, *, msg: str = '错误代码:500 Internal Server Error', data: Any = None):
        super().__init__(msg=msg, data=data)


class GatewayError(BaseExceptionMixin):
    """
    网关错误
    """
    code = 502

    def __init__(self, *, msg: str = '错误代码:502 Bad Gateway', data: Any = None):
        super().__init__(msg=msg, data=data)


class CodeError(BaseExceptionMixin):

    def __init__(self, *, error: CodeEnum, data: Any = None):
        self.code = error.code
        super().__init__(msg=error.msg, data=data)


class AuthorizationError(BaseExceptionMixin):
    """
    授权错误
    """
    code = 401

    def __init__(self, *, msg: str = '权限被拒绝', data: Any = None):
        super().__init__(msg=msg, data=data)


class TokenError(BaseExceptionMixin):
    """
    Token令牌错误
    """
    code = 401

    def __init__(self, *, msg: str = 'Token令牌无效', data: Any = None):
        super().__init__(msg=msg, data=data)


class TokenAuthError(Exception):
    """
    Token令牌身份验证错误
    """

    def __init__(self, err_desc: str = "Token令牌身份验证错误"):
        self.err_desc = err_desc


class TokenExpired(Exception):
    """
    Token令牌已过期
    """

    def __init__(self, err_desc: str = "Token令牌已过期"):
        self.err_desc = err_desc


class AuthenticationError(Exception):
    """
    权限被拒绝
    """

    def __init__(self, err_desc: str = "身份验证错误"):
        self.err_desc = err_desc


class RESOURCE_ERROR(BaseExceptionMixin):
    """
    资源不存在
    """
    code = 40001

    def __init__(self, *, msg: str = '资源不存在', data: Any = None):
        super().__init__(msg=msg, data=data)


class SYSTEM_ERROR(BaseExceptionMixin):
    """
    错误code
    """
    code = 50000

    def __init__(self, *, msg: str = '错误code', data: Any = None):
        super().__init__(msg=msg, data=data)


class SQL_ERROR(BaseExceptionMixin):
    """
    错误sql
    """
    code = 50005

    def __init__(self, *, msg: str = '错误sql', data: Any = None):
        super().__init__(msg=msg, data=data)
