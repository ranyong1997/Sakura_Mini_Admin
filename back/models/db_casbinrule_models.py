#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 11:45
# @Author  : 冉勇
# @Site    : 
# @File    : db_casbinrule_models.py
# @Software: PyCharm
# @desc    : 权限规则数据库
from back.app.database import Base
from sqlalchemy import String, Column, Integer


class CasbinRule(Base):
    __tablename__ = 'casbin_rule'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))