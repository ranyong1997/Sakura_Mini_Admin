#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 11:43
# @Author  : 冉勇
# @Site    : 
# @File    : db_requests_log.py
# @Software: PyCharm
# @desc    : Http请求日志
from datetime import datetime
from back.dbdriver.mysql import Base
from sqlalchemy import String, Column, Integer, DateTime, JSON


class RequestLog(Base):
    __tablename__ = 'request_log'
    id = Column(Integer, primary_key=True)
    method = Column(String(10))
    url = Column(String(255))
    headers = Column(JSON)
    params = Column(JSON)
    JSON = Column(JSON)
    timestamp = Column(DateTime, default=datetime.now)
