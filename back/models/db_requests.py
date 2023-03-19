#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 11:43
# @Author  : 冉勇
# @Site    : 
# @File    : db_requests.py
# @Software: PyCharm
# @desc    :
from datetime import datetime
from back.dbdriver.mysql import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Requests(Base):
    __tablename__ = 'requests'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    url = Column(String(128), nullable=False, unique=True, comment='URI')
    method = Column(String(128), nullable=False, unique=True, comment='方法')
    headers = Column(String(128), nullable=True, comment='请求头')
    params = Column(String(128), nullable=True, comment='参数')
    data = Column(String(128), nullable=True, comment='data')
    json = Column(String(128), nullable=True, comment='json')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cas')
