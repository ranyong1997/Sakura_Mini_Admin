#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:15
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    : 判断环境
import json
from back.utils.logger import log
from enum import Enum

ENV = None


class Environment(Enum):
    PRODUCT = "product"
    TEST = "test"


with open('store/env.json', 'r') as f:
    ENV = json.loads(f.read()).get('env', 'test')

if ENV == Environment.PRODUCT.value:
    log.info("当前环境为 生产 环境！")
    from back.environment.product import *
elif ENV == Environment.TEST.value:
    log.info("当前环境为 测试 环境！")
    from back.environment.test import *
else:
    raise ValueError("不识别的环境配置，正式环境请使用：product， 测试环境请使用：test")
