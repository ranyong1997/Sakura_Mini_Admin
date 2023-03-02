#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/28 15:30
# @Author  : 冉勇
# @Site    : 
# @File    : user_services.py
# @Software: PyCharm
# @desc    :
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.orm import Session
from back.app import settings
from back.app.database import SessionLocal
from back.crud import services
from back.models.db_user_models import User
from back.utils import password, token
from back.utils.exception import errors
from back.utils.redis import redis_client
from back.utils.token import APP_TOKEN_CONFIG


async def login(form_data: OAuth2PasswordRequestForm):
    with SessionLocal() as db:
        current_user = services.get_user_by_username(db, form_data.username)
        if not current_user:
            raise errors.NotFoundError(msg='用户名不存在')
        elif not password.verity_password(form_data.password, current_user.hashed_password):
            raise errors.AuthorizationError(msg='密码错误')
        elif current_user.is_active:
            raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
        # 更新登陆时间
        services.update_user_login_time(db, form_data.username)
        # 创建token
        access_token_expired = timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
        # token过期时间
        access_token = token.create_access_token(data={'sub': form_data.username}, expires_delta=access_token_expired)
        # 将token写入redis,并设置过期销毁时间,创建根目录/Sakura/user
        await redis_client.set(f'{settings.REDIS_PREFIX}:user:{form_data.username}', access_token,
                         ex=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
        return access_token, current_user.is_superuser


def update_avatar(db: Session, current_user: User, avatar: str):
    """
    更新头像
    :param db:
    :param current_user:
    :param avatar:
    :return:
    """
    user = db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=avatar)
    )
    return user.rowcount


def delete_avatar(db: Session, user_id: int) -> int:
    """
    删除头像
    :param db:
    :param user_id:
    :return:
    """
    user = db.execute(
        update(User)
        .where(User.id == user_id)
        .values(avatar=None)
    )
    return user.rowcount
