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
from pathlib import Path
from typing import List

# 项目根目录 父一级再父一级再父一级 root根路径
base_dir = Path(__file__).absolute().parent.parent


class Settings(BaseSettings):
    DEBUG: bool = True  # DEBUG模式
    # 数据库—server
    DB_ECHO: bool = False  # 是否开启日志打印
    MYSQL_HOST: str = None  # 数据库主机
    MYSQL_PORT: int = None  # 数据库端口
    MYSQL_USER: str = None  # 数据库用户名
    MYSQL_PWD: str = None  # 数据库密码
    DBNAME: str = None  # 数据库表名
    MySQL_CHARSET: str = None  # 数据库编码格式
    # Redis-server
    REDIS_OPEN: bool = True  # 是否开启Redis连接
    REDIS_HOST: str = None  # Redis主机
    REDIS_PORT: int = None  # Redis端口
    REDIS_DB: int = None  # Redis数据库
    REDIS_PASSWORD: str = None  # Redis密码
    REDIS_TIMEOUT: int = None  # Redis超时
    # APScheduler Redis
    APS_REDIS_HOST: str = None  # Redis主机
    APS_REDIS_PORT: int = None  # Redis端口
    APS_REDIS_PASSWORD: str = None  # Redis密码
    APS_REDIS_DATABASE: int = None  # Redis数据库
    APS_REDIS_TIMEOUT: int = None  # Redis超时
    # APScheduler Executor (TP:线程，PP:进程)
    APS_TP: bool = True
    APS_TP_EXECUTOR_NUM: int = 10  # 执行数 > 0
    APS_PP: bool = True
    APS_PP_EXECUTOR_NUM: int = 10  # 执行数 > 0
    # APScheduler Default
    APS_COALESCE: bool = False  # 是否合并运行
    APS_MAX_INSTANCES: int = 3  # 最大实例数
    # Email-server
    EMAIL_DESCRIPTION: str = None  # 邮件标题
    EMAIL_SERVER: str = None  # 电子邮件服务器
    EMAIL_PORT: int = None  # 电子邮件端口
    EMAIL_USER: str = None  # 发件人
    EMAIL_PASSWORD: str = None  # 授权密码，非邮箱密码
    EMAIL_SSL: bool = True  # 是否使用ssl
    # sqlalchemy_server
    SQLALCHEMY_DATABASE_URI: str = ''
    # 异步URI
    ASYNC_SQLALCHEMY_URI: str = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Casbin权限控制
    model_path: str = os.path.join(base_dir, './rbac_model.conf')
    # Redis源配置
    REDIS_URI: str = ''
    # Redis键前缀
    REDIS_PREFIX: str = 'Sakura'
    # Captcha验证码超时
    CAPTCHA_EXPIRATION_TIME: int = 60  # 单位：s
    # Cookies
    COOKIES_MAX_AGE: int = 60 * 5  # cookies 时效 60 * 5 = 5 分钟
    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_GZIP: bool = True
    MIDDLEWARE_ACCESS: bool = True
    # 项目标题
    project_title: str = "Sakura_Mini_Admin"
    # Docs文档 正式上线将/docs 改成None
    docs_url: str = "/docs"
    # Redocs文档正式上线将/redocs 改成None
    redoc_url: str = "/redocs"
    # 项目描述
    project_description: str = """
#### Description/说明
<details>
<summary>点击展开/Click to expand</summary>
> [中文/Chinese]
- 🌸Mini后台管理，更多功能正在开发中。
- 本项目开源在[GitHub：Sakura_Mini_Admin](https://github.com/ranyong1997/Sakura_Mini_Admin)。
- 本项目仅供学习交流使用，严禁用于违法用途，如有侵权请联系作者。
</details>
#### Contact author/联系作者
<details>
<summary>点击展开/Click to expand</summary>
- WeChat: RanY_Luck
- Email: [ranyong1209@gmail.com](mailto:ranyong1209@gmail.com)
- Github: [✶  🎀  GitHub地址  🎀  ✶](https://github.com/ranyong1997)
</details>
"""
    # 项目版本
    project_version: str = '0.0.6'
    # host
    server_host: str = "0.0.0.0"
    # port
    server_port: int = 8000
    # 配置允许域名
    # cors_allow_origins: List[str] = ["http://localhost", "http://localhost:5555", "http://127.0.0.1:5555", "http://127.0.0.1:5174"]
    # 所有域名可访问
    cors_allow_origins: List[str] = ["*"]
    # 配置允许访问方式
    cors_allow_methods: List[str] = ["*"]
    # 配置允许访问请求头
    cors_allow_headers: List[str] = ["*"]
    # url的前缀
    url_prefix: str = "/v1/token"
    # jwt加密的key CMD运行: >>>openssl rand -hex 32<<< 生成key
    jwt_secret_key: str = "c71336cfb4c32c0266ba636cf449e71e64e2c3cfe01728182cf5c3ddb33e357b"
    # jwt 加密算法
    jwt_algorithm: str = "HS256"
    # token过期时间，单位：秒 7天过期时间
    jwt_exp_seconds: int = 7 * 24 * 60 * 60
    # 将当前目录添加到系统变量中
    BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))  # 当前项目路径
    LOG_PATH: str = os.path.join(BASE_DIR, '../logs')  # log_path为存放日志的路径
    # 图片上传存放路径: /static/media/uploads/
    ImgPath = os.path.join(base_dir, 'static', 'media', 'uploads')
    # 头像上传存放路径: /static/media/uploads/avatars/
    AvatarPath = os.path.join(ImgPath, 'avatars', '')
    BANNER: str = """
      ____        _                        __  __ _ _   _ _        _       _           _       
 / ___|  __ _| | ___   _ _ __ __ _    |  \/  (_) \ | (_)      / \   __| |_ __ ___ (_)_ __  
 \___ \ / _` | |/ / | | | '__/ _` |   | |\/| | |  \| | |     / _ \ / _` | '_ ` _ \| | '_ \ 
  ___) | (_| |   <| |_| | | | (_| |   | |  | | | |\  | |    / ___ \ (_| | | | | | | | | | |
 |____/ \__,_|_|\_\\__,_|_|  \__,_|___|_|  |_|_|_| \_|_|___/_/   \_\__,_|_| |_| |_|_|_| |_|
                                 |_____|              |_____|                                                                                                                                                                                                              
    """


class DevConfig(Settings):
    # 开发者模式
    class Config:
        env_file = os.path.join(base_dir, "conf", "dev.env")


class ProConfig(Settings):
    # 正式环境
    class Config:
        env_file = os.path.join(base_dir, "conf", "pro.env")


# 获取sakura_mini环境变量
Sakura_Mini_ENV: str = os.environ.get("sakura_mini_env", "dev")
# 如果sakura_mini存在且为pro
Config = ProConfig() if Sakura_Mini_ENV and Sakura_Mini_ENV.lower() == "pro" else DevConfig()
# 初始化 sqlalchemy(由 apscheduler 使用)
Config.SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PWD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.DBNAME}?charset={Config.MySQL_CHARSET}'
# 初始化 sqlalchemy(异步)
Config.ASYNC_SQLALCHEMY_URI = f'mysql+aiomysql://{Config.MYSQL_USER}:{Config.MYSQL_PWD}' \
                              f'@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.DBNAME}'
# 初始化Redis(暂时废除)
Config.REDIS_URI = f'redis://:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}?encoding=utf-8'
