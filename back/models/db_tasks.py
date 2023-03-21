#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 14:08
# @Author  : 冉勇
# @Site    : 
# @File    : db_tasks.py
# @Software: PyCharm
# @desc    :
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union
from pydantic import BaseModel


class Job(BaseModel):
    __tablename__ = 'job'
    __table_args__ = {'extend_existing': True}
    id: Union[str, uuid.UUID]  # 任务id, 必须唯一
    name: Optional[str] = None  # 任务的名字
    func: Optional[str] = None  # 任务的方法映射字符串
    args: Optional[Sequence[Optional[str]]] = None  # 任务的 args参数
    kwargs: Optional[Dict[str, Any]] = None  # 任务的kwargs 参数表
    executor: Optional[str] = 'default'  # 执行期
    jobstore: Optional[str] = 'default'  # 存储器
    misfire_grace_time: Optional[int] = 30  # 任务执行的抖动时间
    coalesce: Optional[bool] = False  # 任务是否合并执行
    max_instances: Optional[int] = 1  # 每个任务的最大实例
    next_run_time: Optional[Union[str, datetime]] = None  # 任务的下次执行时间
