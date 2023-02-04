#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 15:36
# @Author  : 冉勇
# @Site    : 
# @File    : database.py
# @Software: PyCharm
# @desc    : 数据库以及连接的配置
import os
import casbin  # 权限控制模块
from sqlalchemy import create_engine
from back.app import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from casbin_sqlalchemy_adapter import Adapter
from back.app.config import Config

# 创建一个使用内存的SQLite数据库
# SQLALCHEMY_DATABASE_MEMORY = "sqlite+pysqlite:///:memory:"
# engine_test = create_engine(SQLALCHEMY_DATABASE_MEMORY, echo=False, )
# SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# # 组装数据库的绝对地址(数据库生成在一下目录)
# DB_DIR = os.path.join(settings.BASE_DIR, '../Sakura_Mini_Admin_data.db')
#
# # 数据库访问地址
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}"
# # 创建物理SQlite数据库
# engine = create_engine(f'{SQLALCHEMY_DATABASE_URL}?check_same_thread=False', echo=False)
#
# # 启动会话
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建一个使用Mysql数据库
# 创建数据库引擎
engine = create_engine(f'{Config.SQLALCHEMY_DATABASE_URI}', encoding='utf8', echo=False)
# engine = create_engine('mysql+mysqlconnector://sakura_Mini_Admin:phz2kAshAfSfJGrA@120.79.24.202:3306/sakura_mini',
#                        encoding='utf8', echo=False)
with engine.connect() as conn:
    conn.execute(
        "CREATE DATABASE IF NOT EXISTS sakura_mini default character set utf8mb4 collate utf8mb4_unicode_ci")
engine.dispose()

# 创建本地会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
model_path = os.path.join(settings.BASE_DIR, '../rbac_model.conf')


def get_casbin():
    """
    返回一个最新的权限规则
    :return:
    """
    return casbin.Enforcer(model_path, adapter)
