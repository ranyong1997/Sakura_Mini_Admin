#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 15:23
# @Author  : 冉勇
# @Site    : 
# @File    : casbin_object_router.py
# @Software: PyCharm
# @desc    : Casbin资源相关路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from back.app.database import get_db
from back.crud import casbinobject_services
from back.schemas import casbin_schemas
from back.router.v1.user_router import return_rule
from back.models import db_casbin_object_models
from back.utils.token import oauth2_scheme
from back.utils.casbin import verify_enforce

router = APIRouter(
    prefix="/v1",
    tags=["Casbin资源"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


################################
# Casbin资源相关的api接口
################################
@router.get("/co/get_cos")
async def get_cos(db: Session = Depends(get_db)):
    """
    获取Casbin资源
    """
    return casbinobject_services.get_casbin_objects(db)


@router.post("/co/create_co", summary="创建资源")
async def create_casbin_object(co: casbin_schemas.createCasbinObject, token: str = Depends(oauth2_scheme),
                               db: Session = Depends(get_db)):
    """
    创建资源
    """
    if verify_enforce(token, return_rule("CasbinObject", 'create')):
        new_co = db_casbin_object_models.CasbinObject()
        new_co.name = co.name
        new_co.object_key = co.object_key
        new_co.description = co.description
        new_co.user_id = co.user_id
        return casbinobject_services.create_casbin_object(db, new_co)
    else:
        raise no_permission


@router.get("/co/get_co", summary="根据co_id获取资源")
async def get_casbin_object(co_id: int, db: Session = Depends(get_db)):
    """
    根据co_id获取资源
    """
    return casbinobject_services.get_casbin_object_by_id(db, co_id)


@router.post("/co/update_co", summary="更新casbin_object")
async def update_casbin_object_by_id(co: casbin_schemas.EditCasbinObject, token: str = Depends(oauth2_scheme),
                                     db: Session = Depends(get_db)):
    """
    更新casbin_object
    """
    if verify_enforce(token, return_rule("CasbinObject", "update")):
        return casbinobject_services.update_casbin_object(db, co.old_co_id, co.name, co.object_key, co.description)
    else:
        raise no_permission


@router.delete("/co/delete_co",summary="根据co_id删除资源")
async def delete_casbin_object_by_id(co_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    根据co_id删除资源
    """
    if verify_enforce(token, return_rule('CasbinObject', 'read')):
        return casbinobject_services.delete_casbin_object_by_id(db, co_id)
    else:
        raise no_permission
