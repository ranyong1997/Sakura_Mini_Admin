#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 15:56
# @Author  : 冉勇
# @Site    : 
# @File    : casbin_router.py
# @Software: PyCharm
# @desc    : Casbin权限验证路由
from fastapi import APIRouter, Depends, HTTPException, status
from back.schemas import user_schemas
from back.utils.token import oauth2_scheme
from back.utils.casbin import verify_enforce

router = APIRouter(
    prefix="/v1",
    tags=["Casbin权限验证"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


################################
# Casbin权限验证的api接口
################################
@router.get("/get_menu")
async def get_menu_permissions(token: str = Depends(oauth2_scheme)):
    """
    获取菜单权限
    """
    rules = [
        ['User', 'show'],
        ['Role', 'show'],
        ['CasbinObject', 'show'],
        ['CasbinAction', 'show']
    ]
    menu = {}
    for r in rules:
        if verify_enforce(token, user_schemas.Casbin_rule(obj=r[0], act=r[1])):
            menu[r[0]] = True
        else:
            menu[r[0]] = False
    return menu


@router.post('/isAuthenticated')
async def isAuthenticated(rule: user_schemas.Casbin_rule, token: str = Depends(oauth2_scheme)):
    """
    路由页面的权限验证接口
    """
    return verify_enforce(token, rule)
