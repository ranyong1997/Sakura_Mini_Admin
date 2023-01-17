#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:38
# @Author  : 冉勇
# @Site    : 
# @File    : config.py
# @Software: PyCharm
# @desc    : 全局配置文件
import os
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    # DEBUG模式
    debug: bool = True
    # 项目标题
    project_title = "Sakura_Mini_Admin"
    # 项目描述
    project_description: str = "欢迎来到Sakura_Mini_Admin后台管理系统,一个简洁轻快的后台管理框架.支持拥有多用户组的RBAC管理后台 🚀"
    # 项目版本
    project_version: str = '0.0.2'
    # host
    server_host: str = "127.0.0.1"
    # port
    server_port: int = 5555
    # 配置允许域名
    origins: List[str] = ["http://localhost", "http://localhost:5555", "http://127.0.0.1:5555"]
    # 配置允许访问方式
    cors_allow_methods: List[str] = ["PUT", "POST", "GET", "DELETE", "OPTIONS"]
    # 配置允许访问请求头
    cors_allow_headers: List[str] = ["*"]
    # url的前缀
    url_prefix: str = "/v1/token"
    # jwt加密的key >>>openssl rand -hex 32<<<
    jwt_secret_key: str = "c71336cfb4c32c0266ba636cf449e71e64e2c3cfe01728182cf5c3ddb33e357b"
    # jwt 加密算法
    jwt_algorithm: str = "HS256"
    # token过期时间，单位：秒
    jwt_exp_seconds: int = 7 * 24 * 60 * 60
    # 将当前目录添加到系统变量中
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))  # 当前项目路径
    LOG_PATH = os.path.join(BASE_DIR, '../logs')  # log_path为存放日志的路径
    BANNER: str = """
      ____        _                        __  __ _ _   _ _        _       _           _       
 / ___|  __ _| | ___   _ _ __ __ _    |  \/  (_) \ | (_)      / \   __| |_ __ ___ (_)_ __  
 \___ \ / _` | |/ / | | | '__/ _` |   | |\/| | |  \| | |     / _ \ / _` | '_ ` _ \| | '_ \ 
  ___) | (_| |   <| |_| | | | (_| |   | |  | | | |\  | |    / ___ \ (_| | | | | | | | | | |
 |____/ \__,_|_|\_\\__,_|_|  \__,_|___|_|  |_|_|_| \_|_|___/_/   \_\__,_|_| |_| |_|_|_| |_|
                                 |_____|              |_____|                                                                                                                                                                                                              
    """
