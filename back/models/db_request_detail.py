#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/20 14:38
# @Author  : 冉勇
# @Site    : 
# @File    : db_request_detail.py
# @Software: PyCharm
# @desc    : Http请求信息
from back.dbdriver.mysql import Base
from sqlalchemy import String, Column, Integer, JSON


class RequestDetail(Base):
    __tablename__ = 'request_detail'
    id = Column(Integer, primary_key=True)
    status_code = Column(Integer)
    text = Column(String(255))
    json = Column(JSON)
