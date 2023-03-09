#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 15:36
# @Author  : 冉勇
# @Site    : 
# @File    : mysql.py
# @Software: PyCharm
# @desc    : 数据库以及连接的配置
import sys
import casbin  # 权限控制模块
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from casbin_sqlalchemy_adapter import Adapter
from back.app.config import Config
from back.utils.logger import log

# 创建一个使用Mysql数据库
# 创建数据库引擎
try:
    engine = create_engine(f'{Config.SQLALCHEMY_DATABASE_URI}', echo=Config.DB_ECHO, pool_recycle=1500, future=True)
    log.debug(f"连接同步数据库:{Config.MYSQL_HOST}, -- {Config.DBNAME} -- {Config.MYSQL_USER} -- {Config.MYSQL_PWD}")
except Exception as e:
    log.error('❌ 数据库链接失败 {}', e)
    sys.exit()
else:
    # 创建本地会话
    SessionLocal = sessionmaker(expire_on_commit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取一个数据库，异步fastapi下使用
    :return: session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 数据模型的基类
Base = declarative_base()

# casbin相关配置
adapter = Adapter(engine)
model_path = Config.model_path


def get_casbin():
    """
    返回一个最新的权限规则
    :return:
    """
    return casbin.Enforcer(model_path, adapter)
