#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 17:04
# @Author  : 冉勇
# @Site    : 
# @File    : db_casbin_object_models.py
# @Software: PyCharm
# @desc    : 权限资源数据库
from datetime import datetime
from back.app.database import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class CasbinObject(Base):
    __tablename__ = 'casbin_object'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='资源名称')
    object_key = Column(String(128), nullable=False, unique=True, comment='资源标识')
    description = Column(String(128), nullable=True, comment='资源描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cos')
