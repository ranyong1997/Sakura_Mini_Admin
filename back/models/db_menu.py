#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/5 10:58
# @Author  : 冉勇
# @Site    : 
# @File    : db_menu.py
# @Software: PyCharm
# @desc    :
from datetime import datetime
from back.dbdriver.mysql import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Menu(Base):
    __tablename__ = 'menu'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='菜单名称')
    path = Column(String(128), nullable=False, unique=True, comment='菜单url')
    icon = Column(String(128), nullable=True, comment='菜单图标')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cos')