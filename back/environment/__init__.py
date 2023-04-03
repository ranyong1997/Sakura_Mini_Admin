#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:15
# @Author  : 冉勇
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @desc    : 判断环境
import json
from enum import Enum

ENV = None


class Environment(Enum):
    PRODUCT = "product"
    TEST = "test"


# todo:将获取env.json 写入到config.py里面,方便配置
with open('back/store/env.json', 'r') as f:
# with open('store/env.json', 'r') as f:
        ENV = json.loads(f.read()).get('env', 'test')

if ENV == Environment.PRODUCT.value:
    from back.environment.product import *
elif ENV == Environment.TEST.value:
    from back.environment.test import *
else:
    raise ValueError("不识别的环境配置，正式环境请使用：product， 测试环境请使用：test")
