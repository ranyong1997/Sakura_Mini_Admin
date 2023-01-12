#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 11:31
# @Author  : 冉勇
# @Site    : 
# @File    : user_token.py
# @Software: PyCharm
# @desc    : 用户路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from back.app.database import get_db
from back.schemas import user_schemas
from back.schemas.user_schemas import User, Casbin_rule, Users, UserUpdate, ChangeUserRole
from back.utils.password import get_password_hash
from back.utils.token import oauth2_scheme, get_username_by_token
from back.utils.casbin import verify_enforce
from back.crud import crud

router = APIRouter(
    prefix="v1",
    tags=["v1"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


def return_rule(obj, act):
    """
    返回一个验证权限的规则，包括obj、act。
    :param obj:
    :param act:
    :return:
    """
    return Casbin_rule(obj=obj, act=act)


################################
# User相关的api接口
################################
@router.post("/user/create_user")
async def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    创建用户
    :param user:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名称重复",
        headers={"WWW-Authenticate": "Bearer"}
    )
    # 注册用户名称不能与用户组的role_key重复
    role = crud.get_role_by_role_key(db, user.username)
    if role:
        raise credentials_exception
    return crud.create_user(db, user.username, user.password, user.sex, user.email)


@router.get("/user/me", response_model=User)
async def read_user_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    返回当前用户的资料
    :param token:
    :param db:
    :return:
    """
    username = get_username_by_token(token)
    return crud.get_user_by_username(db, username)


@router.get("/user/user_by_id", response_model=User)
async def get_user_by_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
     根据id获取用户资料
    :param token:
    :param db:
    :param user_id:
    :return:
    """
    if verify_enforce(token, return_rule("User", "read")):
        return crud.get_user_by_id(db, user_id)
    else:
        raise no_permission


@router.get("/user/get_users", response_model=Users)
async def get_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 10,
                    keyword: str = ""):
    """
    获取用户
    :param db:
    :param skip: 页码
    :param limit: 条数
    :param keyword: 关键字
    :return:
    """
    users = Users(users=crud.get_users(db, skip, limit, keyword), count=crud.get_users_count_by_keyword(db, keyword))
    return users


@router.get("/users/active_change")
async def user_active_change(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    修改用户锁定
    :param token:
    :param db:
    :param user_id:
    :return:
    """
    if verify_enforce(token, return_rule('User', 'update')):
        return crud.active_change(db, user_id)
    else:
        raise no_permission


@router.get("/user/delete_user")
async def delete_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    根据id删除用户
    :param token:
    :param db:
    :param user_id:
    :return:
    """
    if verify_enforce(token, return_rule("User", "delete")):
        return crud.delete_user_by_id(db, user_id)
    else:
        raise no_permission


@router.post("/user/update_user")
async def update_user(user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户资料
    :param user:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule("User", "update")):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名称重复!",
            headers={"WWW-Authenticate": "Bearer"}
        )
        u = crud.get_user_by_id(db, user.user_id)
        # 修改用户名称不能与用户组的role_key重复
        role = crud.get_role_by_role_key(db, user.username)
        if role:
            raise credentials_exception
        u.username = user.username
        u.sex = user.sex
        u.remark = user.remark
        u.avatar = user.avatar
        if user.password != "":
            hashed_password = get_password_hash(user.password)
            u.hashed_password = hashed_password
        try:
            db.commit()
            return True
        except:
            return False
    else:
        raise no_permission


@router.post("/user/update_me")
async def update_me(user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户资料
    :param user:
    :param token:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据!",
        headers={"WWW-Authenticate": "Bearer"}
    )
    username = get_username_by_token(token)
    me = crud.get_user_by_username(db, username)
    if user.user_id == me.id:
        u = crud.get_user_by_id(db, user.user_id)
        u.username = user.username
        u.email = user.email
        u.sex = user.sex
        u.avatar = user.avatar
        if user.password != "":
            hashed_password = get_password_hash(user.password)
            u.hashed_password = hashed_password
        try:
            db.commit()
            return True
        except:
            raise credentials_exception
    else:
        return no_permission


@router.post("/user/change_user_role")
async def change_user_role(data: ChangeUserRole, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户拥有的用户组
    :param data:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule('User', 'update')):
        # 将用户组名称改成role_key
        role_keys = []
        for name in data.names:
            role = crud.get_role_by_name(db, name)
            role_keys.append(role.role_key)
        return crud.change_user_role(db, data.user_id, role_keys)
    else:
        raise no_permission


@router.get("/user/get_user_role")
async def get_user_role(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取用户所拥有的用户组
    :param user_id:
    :param token:
    :param db:
    :return:
    """
    if verify_enforce(token, return_rule("User", "read")):
        user = crud.get_user_by_id(db, user_id)
        roles = crud.get_roles(db)
        options = []  # 所有权限组名称
        for role in roles:
            options.append(role.name)
        checkeds = []  # 当前用户所拥有的用户组
        crs = crud.get_casbin_rules_by_username(db, user.username)
        for cr in crs:
            role = crud.get_role_by_role_key(db, cr.v1)
            checkeds.append(role.name)
        return {'options': options, 'checkeds': checkeds}
    else:
        raise no_permission