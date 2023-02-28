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
    user = db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=avatar)
    )
    return user.rowcount
