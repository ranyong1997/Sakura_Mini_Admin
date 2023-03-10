#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 14:39
# @Author  : 冉勇
# @Site    : 
# @File    : role_router.py
# @Software: PyCharm
# @desc    : 角色路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from back.dbdriver.mysql import get_db
from back.crud import role_services, casbinobject_services, casbinaction_services, casbinrule_services
from back.router.v1.user_router import return_rule
from back.models import db_role_models, db_casbinrule_models
from back.utils.token import oauth2_scheme
from back.utils.casbin import verify_enforce
from back.schemas import role_schemas

router = APIRouter(
    prefix="/v1",
    tags=["角色"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


################################
# role相关的api接口
################################
@router.get("/role/get_roles", summary="获取角色")
async def get_roles(db: Session = Depends(get_db)):
    """
    获取角色
    """
    return role_services.get_roles(db)


@router.post("/role/create_role", summary="创建角色")
async def create_role(role: role_schemas.Role, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    创建角色
    """
    if verify_enforce(token, return_rule('Role', 'create')):
        new_role = db_role_models.Role()
        new_role.name = role.name
        new_role.role_key = role.role_key
        new_role.description = role.description
        new_role.user_id = int(role.user_id)
        return role_services.create_role(db, new_role)
    else:
        raise no_permission


@router.get("/role/get_role_by_id", summary="根据id获取角色")
async def get_role_by_id(role_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    根据id获取角色
    """
    if verify_enforce(token, return_rule('Role', 'read')):
        return role_services.get_role_by_id(db, role_id)
    else:
        raise no_permission


@router.post("/role/update_role", summary="修改角色")
async def update_role_by_id(role: role_schemas.EditRole, token: str = Depends(oauth2_scheme),
                            db: Session = Depends(get_db)):
    """
    修改角色
    """
    if verify_enforce(token, return_rule('Role', 'update')):
        new_role = db_role_models.Role()
        new_role.name = role.name
        new_role.role_key = role.role_key
        new_role.description = role.description
        return role_services.update_role_by_id(db, role.old_role_id, new_role)
    else:
        raise no_permission


@router.delete("/role/delete_role", summary="根据id删除角色")
async def delete_role_by_id(role_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    根据id删除角色
    """
    if verify_enforce(token, return_rule('Role', 'delete')):
        return role_services.delete_role_by_id(db, role_id)
    else:
        raise no_permission


@router.get("/role/get_coca", summary="返回用户组role所包含的权限用于前端使用多选框来展示")
async def get_co_ca(role_id: int, db: Session = Depends(get_db)):
    """
    返回用户组role所包含的权限用于前端使用多选框来展示
    """
    cos = casbinobject_services.get_casbin_objects(db)
    cas = casbinaction_services.get_casbin_actions(db)
    role = role_services.get_role_by_id(db, role_id)
    all_co_ca = []  # 拼装所有权限的列表
    co_key_name = {}  # 组装一个字典,里面的资源key对应name
    ca_key_name = {}  # 组装一个字典，里面的动作key对应name
    # 一个临时例子
    # ['用户管理', '增', '用户管理', '删', '用户管理', '改', '用户管理', '增', '用户管理', '删', '用户管理', '改']
    cks = []
    checkeds = []  # 当前用户组所拥有的权限
    for co in cos:
        coca = [co.name]
        for ca in cas:
            coca.append(ca.name)
        all_co_ca.append(coca)
    for co in cos:
        co_key_name[co.object_key] = co.name
    for ca in cas:
        ca_key_name[ca.action_key] = ca.name
    crs = casbinrule_services.get_casbin_rules_by_role_key(db, role.role_key)
    for cr in crs:
        cks.append(co_key_name[cr.v1])
        cks.append(ca_key_name[cr.v2])
    temp_names = []
    for ck in cks:
        if len(temp_names) == 0:
            temp_names.append(ck)
        elif temp_names[0] == ck:
            pass
        elif ck in co_key_name.values() and ck != temp_names[0]:
            checkeds.append(temp_names)
            temp_names = [ck]
        elif ck in ca_key_name.values() and ck not in temp_names:
            temp_names.append(ck)
    checkeds.append(temp_names)
    return {'options': all_co_ca, 'checkeds': checkeds}


@router.post("/role/change_role", summary="修改用户组所拥有的的权限")
async def change_role(cr_data: role_schemas.ChangeRole, token: str = Depends(oauth2_scheme),
                      db: Session = Depends(get_db)):
    """
    修改用户组所拥有的的权限
    """
    if verify_enforce(token, return_rule('Role', 'update')):
        role = role_services.get_role_by_id(db, cr_data.role_id)
        cos = casbinobject_services.get_casbin_objects(db)
        cas = casbinaction_services.get_casbin_actions(db)
        co_name_key = {}  # 组装一个字典，里面的资源name对应key
        ca_name_key = {}  # 组装一个字典，里面的资源name对应key
        change_crs = []  # 准备要更新添加所有casbinrule
        for co in cos:
            co_name_key[co.name] = co.object_key
        for ca in cas:
            ca_name_key[ca.name] = ca.action_key
        for crs in cr_data.checkeds:
            if crs:
                try:
                    object_key = co_name_key[crs[0]]
                except:
                    return False
                cr_name = crs[0]
                if len(crs) <= 1:
                    return False
                for cr in crs:
                    if cr != cr_name:
                        change_crs.append(db_casbinrule_models.CasbinRule(ptype='p', v0=role.role_key, v1=object_key,
                                                                          v2=ca_name_key[cr]))
        return role_services.change_role_casbinrules(db, role.role_key, change_crs)
    else:
        raise no_permission
