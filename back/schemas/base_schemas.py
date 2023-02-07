#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/6 15:58
# @Author  : 冉勇
# @Site    : 
# @File    : base_schemas.py
# @Software: PyCharm
# @desc    : 基本模式
from back.exception.error import ParamsError


class SakuraModel(object):
    @staticmethod
    def not_empty(v):
        if isinstance(v, str) and len(v.strip()) == 0:
            raise ParamsError("不能为空")
        if isinstance(v, int) or v:
            return v
        else:
            raise ParamsError("不能为空")

    @property
    def parameters(self):
        raise NotImplementedError
