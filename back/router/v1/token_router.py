#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 09:08
# @Author  : 冉勇
# @Site    : 
# @File    : token_router.py
# @Software: PyCharm
# @desc    : 访问令牌路由
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from back.app import settings
from back.dbdriver.mysql import get_db
from back.crud import user_services
from back.schemas.token_schemas import Token
from back.utils import token
from back.utils.password import verify_password
from back.dbdriver.redis import redis_client
from back.utils.token import APP_TOKEN_CONFIG

router = APIRouter(
    prefix="/v1",
    tags=["系统登录"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


################################
# access_token 系统登录相关的api接口
################################


def authenticate_user(db: Session, username: str, password: str):
    """
    认证用户，包括检测用户是否存在，密码校验
    """
    user = user_services.get_user_by_username(db, username=username)  # 获取用户信息
    # 判断用户是否存在
    if not user:
        return False
    # 校验密码失败
    if not verify_password(password, user.hashed_password):
        return False
    # 成功返回User
    return user


@router.post("/token", response_model=Token, summary="获取token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    获取token，如果没有或者密码错误并提示
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    # 判断是否有用户
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户或密码错误!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # token过期时间
    access_token_expired = timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 生成token
    access_token = token.create_access_token(data={'sub': user.username}, expires_delta=access_token_expired)
    # 将token写入redis,并设置过期销毁时间,创建根目录/Sakura/user
    await redis_client.set(f'{settings.REDIS_PREFIX}:user:{user.username}', access_token,
                           ex=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token, "token_type": "bearer"}
