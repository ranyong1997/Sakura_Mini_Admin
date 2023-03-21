#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/9 15:47
# @Author  : 冉勇
# @Site    : 
# @File    : common.py
# @Software: PyCharm
# @desc    : 公共组件
import json
import decimal
from dateutil import tz
from datetime import datetime, timedelta
from typing import Union, Optional, List, Dict
from pytz.tzinfo import DstTzInfo
from sqlalchemy.orm import Session
from fastapi import HTTPException

tz_sh = tz.gettz('Asia/Shanghai')


# json 序列化 特殊对象处理
class MyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, timedelta)):
            return str(obj)
        elif isinstance(obj, DstTzInfo):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


# 字典列表 合并
def _cal_index_key(rec: dict, index_name: Union[str, list]) -> str:
    if isinstance(index_name, list):
        sk = '_'.join(rec[i] for i in index_name)
    else:
        sk = rec[index_name]
    return sk


def combine(recodes: list, pre_recodes: List, index_key: Union[str, list], default: Optional[Dict] = None) -> list:
    pre_map = {}
    for prec in pre_recodes:
        # 这样即使要融入数据 是多个也能很好的 整合在一起
        pre_map.setdefault(_cal_index_key(prec, index_key), {}).update(prec)
    for rec in recodes:
        sk = _cal_index_key(rec, index_key)
        if sk in pre_map:
            if any(set(rec.keys()).intersection(set(pre_map[sk])).difference(
                    index_key if isinstance(index_key, list) else [index_key])):
                raise
            else:
                rec.update(pre_map[sk])
        else:
            # 没有就使用默认值
            if default is not None:
                rec.update(default)
    return recodes


def paginate(db: Session, model: any, page: int = 1, page_size: int = 10):
    """
    分页查询
    :param db: 数据库
    :param model: 数据库库名【User】
    :param page:
    :param page_size:
    :return:
    """
    offset = (page - 1) * page_size
    query = db.query(model).offset(offset).limit(page_size).all()
    if not query:
        raise HTTPException(status_code=404, detail="Items not found")
    return query
