#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/28 15:30
# @Author  : 冉勇
# @Site    : 
# @File    : user_services.py
# @Software: PyCharm
# @desc    :
from sqlalchemy import update
from sqlalchemy.orm import Session
from back.models.db_user_models import User


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
