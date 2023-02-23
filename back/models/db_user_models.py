#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 15:51
# @Author  : 冉勇
# @Site    : 
# @File    : db_user_models.py
# @Software: PyCharm
# @desc    : 用户数据库
from datetime import datetime
from back.app.database import Base
from sqlalchemy import String, Column, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    # 若有多个类指向同一张表，那么在后边的类需要把 extend_existing设为True，表示在已有列基础上进行扩展
    # 或者换句话说，sqlalchemy 允许类是表的字集，如下：
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(32), nullable=False, unique=True, comment='用户昵称')
    hashed_password = Column(String(128), nullable=False, comment='用户密码')
    sex = Column(String(1), nullable=False, default='1', comment='用户性别')
    email = Column(String(128), nullable=False, unique=True, comment='用户邮箱')
    is_superuser = Column(Boolean, default=False, comment='超级权限')  # 1为超管
    is_active = Column(Boolean, default=False, comment='用户账户状态')  # 1为正常
    avatar = Column(String(128), comment='用户头像')
    remark = Column(String(128), comment='备注')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    roles = relationship('Role', uselist=True, back_populates='user')
    cos = relationship('CasbinObject', uselist=True, back_populates='user')
    cas = relationship('CasbinAction', uselist=True, back_populates='user')
