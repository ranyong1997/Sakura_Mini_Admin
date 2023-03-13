#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:30
# @Author  : 冉勇
# @Site    : 
# @File    : db_config.py
# @Software: PyCharm
# @desc    : 业务的数据库配置【测试环境】
from back.app.config import Config

BusinessConfig = {
    "default": {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "pwd": Config.MYSQL_PWD,
        "db": Config.DBNAME,
        "recycle": 30
    },
}

# apscheduler的数据库配置
ApsMysqlConfig = {
    "host": Config.MYSQL_HOST,
    "port": Config.MYSQL_PORT,
    "user": Config.MYSQL_USER,
    "pwd": Config.MYSQL_PWD,
    "db": Config.DBNAME,
    "recycle": 30
}

# DB  表明到数据库的映射
TABLE_DB_MAP = {
    'table_name': "default"
}
