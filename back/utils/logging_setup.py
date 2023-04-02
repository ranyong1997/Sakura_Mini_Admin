#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/1 10:02
# @Author  : 冉勇
# @Site    :
# @File    : logging_setup.py
# @Software: PyCharm
# @desc    : 日志安装
import logging

# 记录日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_root_logger():
    """应用程序根记录器的设置配置"""

    # 获取根记录器实例
    logger = logging.getLogger('')

    # 为记录器配置格式化程序
    formatter = logging.Formatter(LOG_FORMAT)

    # 配置控制台处理程序
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    # 配置 rotating 文件 handler
    file = logging.handlers.RotatingFileHandler(filename="logs/fastapi-elk-stack.log", mode='a',
                                                maxBytes=15000000, backupCount=5)
    file.setFormatter(formatter)

    # 添加处理程序
    logger.addHandler(console)
    logger.addHandler(file)

    # 配置记录器级别
    logger.setLevel(logging.INFO)
