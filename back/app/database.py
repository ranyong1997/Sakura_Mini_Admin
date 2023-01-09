#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 15:36
# @Author  : 冉勇
# @Site    : 
# @File    : database.py
# @Software: PyCharm
# @desc    : 数据库以及连接的配置
import os
import sys
import casbin  # 权限控制模块
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from casbin_sqlalchemy_adapter import Adapter

# 将当前目录添加到系统变量中
BASE_DIR = os.path.join(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 创建一个使用内存的SQLite数据库
# TODO:后续介入mysql
SQLALCHEMY_DATABASE_MEMORY = "sqlite+pysqlite:///:memory:"
engind_test = create_engine(SQLALCHEMY_DATABASE_MEMORY, echo=False)
SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engind_test)


def get_db_test():
    """
    获取一个数据连接，异步fastapi使用
    :return: session
    """
    db = SessionLocal_test()
    try:
        yield db
    finally:
        db.close()


# 组装数据库的绝对地址
DB_DIR = os.path.join(BASE_DIR, "MiniAdmin_data.db")
# 数据库访问地址
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}"
# 创建物理SQlite数据库
engind = create_engine(f"{SQLALCHEMY_DATABASE_URL}?check_same_thread=False", echo=False)

# 启动会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engind)


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
adapter = Adapter(engind)
model_path = os.path.join(BASE_DIR, 'rbac_model.conf')


def get_casbin():
    """
    返回一个
    :return:
    """
    return casbin.Enforcer(model_path, adapter)
