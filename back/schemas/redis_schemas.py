#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/7 16:44
# @Author  : 冉勇
# @Site    : 
# @File    : redis_schemas.py
# @Software: PyCharm
# @desc    :
from datetime import date
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def generate_id():
    return str(uuid4())


def generate_date():
    return str(date.today())


class Product(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    price: float
    created_at: date = Field(default_factory=generate_date)


class Item(BaseModel):
    title: str
    description: Optional[str] = None
