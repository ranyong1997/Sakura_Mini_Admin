#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 16:01
# @Author  : 冉勇
# @Site    : 
# @File    : db_role_models.py
# @Software: PyCharm
# @desc    : 角色数据库
from datetime import datetime
from back.app.database import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='角色id')
    name = Column(String(32), nullable=False, unique=True, comment='角色名称')
    role_key = Column(String(128), nullable=False, unique=True, comment='角色标识')
    description = Column(String(128), nullable=False, comment='角色描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='roles')
