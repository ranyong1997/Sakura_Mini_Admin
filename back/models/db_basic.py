#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/7 09:49
# @Author  : 冉勇
# @Site    : 
# @File    : db_basic.py
# @Software: PyCharm
# @desc    :
import json
from datetime import datetime
from back.models import Base
from typing import Tuple
from decimal import Decimal
from sqlalchemy import INT, Column, BIGINT, TIMESTAMP


class SakuraBase(Base):
    id = Column(INT, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    deleted_at = Column(BIGINT, nullable=False, default=0)
    create_user = Column(INT, nullable=False)
    update_user = Column(INT, nullable=False)
    __abstract__ = True
    __fields__: Tuple[Column] = [id]
    __tag__ = "未定义"
    __alias__ = dict(name="名称")
    __show__ = 1

    def __init__(self, user, id=None):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.create_user = user
        self.update_user = user
        self.deleted_at = 0
        # self.id = id

    def serialize(self, *ignore):
        """
        dump self
        :return:
        """
        data = dict()
        for c in self.__table__.columns:
            if c.name in ignore:
                # 如果字段忽略, 则不进行转换
                continue
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                data[c.name] = val.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(val, Decimal):
                data[c.name] = str(val)
            elif isinstance(val, bytes):
                data[c.name] = val.decode(encoding='utf-8')
            else:
                data[c.name] = val
        return json.dumps(data, ensure_ascii=False)
