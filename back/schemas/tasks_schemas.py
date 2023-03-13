#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 14:08
# @Author  : 冉勇
# @Site    : 
# @File    : tasks_schemas.py
# @Software: PyCharm
# @desc    :
import enum
import uuid
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from back.models.db_tasks import Job


class RequestJob(Job):
    replace_existing: bool = False
    trigger: Optional[str] = None
    trigger_args: Optional[Dict] = None


# 触发器
class TriggerEnum(str, enum.Enum):
    date = "date"
    interval = "interval"
    cron = "cron"


class Rescheduler(BaseModel):
    id: Union[str, uuid.UUID]
    trigger: TriggerEnum
    trigger_args: Optional[Dict[str, Any]]


class BaseResponse(BaseModel):
    message: str
    status_code: Union[int, str]


class QueryResponse(BaseResponse):
    jobs: List[Job]


class OperateResponse(BaseResponse):
    type: str
