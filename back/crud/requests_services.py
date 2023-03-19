#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 11:50
# @Author  : 冉勇
# @Site    : 
# @File    : requests_services.py
# @Software: PyCharm
# @desc    :
from sqlalchemy.orm import Session
from back.models.db_requests import Requests


def create_requests(db: Session, requests: Requests):
    """
    创建Request表
    :param db:
    :param requests:
    :return:
    """
    db.add(requests)
    try:
        db.commit()
        return requests
    except Exception:
        return False