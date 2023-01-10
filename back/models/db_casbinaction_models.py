#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 11:36
# @Author  : 冉勇
# @Site    : 
# @File    : db_casbinaction_models.py
# @Software: PyCharm
# @desc    : 权限动作数据库
from datetime import datetime
from back.app.database import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class CasbinAction(Base):
    __tablename__ = 'casbin_action'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='动作名称')
    action_key = Column(String(128), nullable=False, unique=True, comment='动作标识')
    description = Column(String(128), nullable=True, unique=True, comment='动作描述')
    created_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cas')
