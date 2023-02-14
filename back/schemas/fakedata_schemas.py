#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 10:15
# @Author  : 冉勇
# @Site    : 
# @File    : fakedata_schemas.py
# @Software: PyCharm
# @desc    : 虚拟数据接口
from enum import Enum


class FakeData(str, Enum):
    name = "name"
    address = "address"
    text = "text"
    company = "company"
    user_agent = "user_agent"
    credit_card_full = "credit_card_full"
    free_email = "free_email"
    ssn = "ssn"
    social = "social"
    organization = "organization"
    phone_number = "phone_number"