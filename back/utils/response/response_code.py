#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/21 17:12
# @Author  : 冉勇
# @Site    : 
# @File    : response_code.py
# @Software: PyCharm
# @desc    : 自定义错误码
from enum import Enum


class CodeEnum(Enum):
    """
    自定义错误码
    """
    CAPTCHA_ERROR = (40001, '验证码错误')

    @property
    def code(self):
        """
        获取错误码
        """
        return self.value[0]

    @property
    def msg(self):
        """
        获取错误码码信息
        """
        return self.value[1]
