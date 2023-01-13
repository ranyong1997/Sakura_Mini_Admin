#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 15:41
# @Author  : 冉勇
# @Site    : 
# @File    : casbin_action_router.py
# @Software: PyCharm
# @desc    : Casbin行为路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from back.app.database import get_db
from back.crud import services
from back.models import db_casbinaction_models
from back.schemas import casbin_schemas
from back.router.v1.user_token import return_rule
from back.utils.token import oauth2_scheme
from back.utils.casbin import verify_enforce

router = APIRouter(
    prefix="/v1",
    tags=["Casbin行为"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


################################
# Casbin行为相关的api接口
################################
@router.get("/ca/get_cas")
async def get_cas(db: Session = Depends(get_db)):
    """
    获取casbin行为
    :param db:
    :return:
    """
    return services.get_casbin_actions(db)


@router.post("/ca/create_ca")
async def create_ca(ca: casbin_schemas.createCasbinAction, token: str = Depends(oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
    创建casbin行为
    :param ca:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule("CasbinAction", "create")):
        new_ca = db_casbinaction_models.CasbinAction()
        new_ca.name = ca.name
        new_ca.action_key = ca.action_key
        new_ca.description = ca.description
        new_ca.user_id = ca.user_id
        return services.create_casbin_action(db, new_ca)
    else:
        raise no_permission


@router.get("/ca/get_ca")
async def get_ca(ca_id: int, db: Session = Depends(get_db)):
    """
    根据ca_id获取casbin行为
    :param ca_id:
    :param db:
    :return:
    """
    return services.get_casbin_action_by_id(db, ca_id)


@router.post("/ca/update_ca")
async def update_ca(ca: casbin_schemas.EditCasbinAction, token: str = Depends(oauth2_scheme),
                    db: Session = Depends(get_db)):
    """
    更新casbin行为
    :param ca:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule("CasbinAction", "update")):
        return services.update_casbin_action_by_id(db, ca.old_ca_id, ca.name, ca.action_key, ca.description)
    else:
        raise no_permission


@router.get("/ca/delete_ca")
async def delete_ca(ca_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    根据ca_id删除casbin行为
    :param ca_id:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule("CasbinAction", "delete")):
        return services.delete_casbin_action_by_id(db, ca_id)
    else:
        raise no_permission
