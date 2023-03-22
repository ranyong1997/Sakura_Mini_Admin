#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 11:30
# @Author  : 冉勇
# @Site    : 
# @File    : registrar.py
# @Software: PyCharm
# @desc    : 注册
import time
import traceback
from fastapi import FastAPI, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from loguru import logger
from pydantic import ValidationError
from back.app import settings
from back.dbdriver.mysql import Base, engine, get_db
from back.crud import user_services
from back.router.v1 import api_v1_router
from back.utils import response_code
from back.utils.core.init_scheduler import scheduler_init
from back.utils.exception import errors
from back.utils.logger import log
from back.dbdriver.redis import redis_client


def register_router(app: FastAPI) -> None:
    """
    注册路由
    :param app:
    :return:
    """
    # 项目API
    app.include_router(
        api_v1_router
    )


def register_init(app: FastAPI) -> None:
    """
    初始化连接
    :param app:
    :return:
    """

    @app.on_event("startup")
    async def startup_event():
        logger.bind(name=None).success(f'{settings.BANNER}')
        logger.bind(name=None).success(
            f"{settings.project_title} 正在运行环境: 【环境】 接口文档: http://{settings.server_host}:{settings.server_port}/docs")

    @app.on_event("startup")
    async def startup_event():
        """
            初始化数据库,建表,Redis
            :return:
            """
        try:
            # 在数据库中生成表结构
            # TODO:将生成数据库异步执行
            Base.metadata.create_all(bind=engine)
            logger.bind(name=None).success("数据库和表创建成功.         ✔")
        except Exception as e:
            logger.bind(name=None).error(f"数据库和表创建失败.          ❌ \n Error:{str(e)}")
            raise
        if settings.REDIS_OPEN:
            # 连接redis
            try:
                await redis_client.init_redis_connect()
                logger.bind(name=None).success("redis连接成功.             ✔")

            except Exception as e:
                logger.bind(name=None).error(f"redis连接失败.          ❌ \n Error:{str(e)}")
                raise
        try:
            # 生成初始化数据，添加了一个超级管理员并赋予所有管理权限，以及一些虚拟的用户。
            user_services.create_data(next(get_db()))
            logger.bind(name=None).success("生成初始化数据成功.         ✔")
        except Exception as e:
            logger.bind(name=None).error(f"生成初始化数据失败.          ❌ \n Error:{str(e)}")
            raise
        try:
            # 初始化 定时器
            await scheduler_init.init_scheduler()
            logger.bind(name=None).success("APScheduler正在运行.       ✔")

        except Exception as e:
            logger.bind(name=None).error(f"初始化APScheduler失败.          ❌ \n Error:{str(e)}")
            raise
        try:
            # 加载静态任务
            # await scheduler_init.add_config_job()
            logger.bind(name=None).success("开始加载静态任务.           ✔")
        except Exception as e:
            logger.bind(name=None).error(f"加载静态任务失败.          ❌ \n Error:{str(e)}")
            raise
        logger.bind(name=None).success(
            f"********************  START:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} ********************")

    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            if settings.REDIS_OPEN:
                # 关闭redis连接
                await redis_client.close()
                logger.bind(name=None).success("关闭redis连接.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"关闭redis连接失败.          ❌ \n Error:{str(e)}")
        try:
            for key, db in scheduler_init.items():
                await db.close()
                logger.bind(name=None).success(f"关闭数据库连接池 {key}.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"闭数据库连接池{key}失败          ❌ \n Error:{str(e)}")

        try:
            for rdb, pool in scheduler_init.items():
                await pool.close()
                logger.bind(name=None).success(f"关闭redis连接池:{rdb}.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"关闭redis连接池:{rdb}失败        ❌ \n Error:{str(e)}")
        try:
            for rdb, pool in scheduler_init.items():
                pool.close()
                logger.bind(name=None).success(f"关闭sync_redis连接池:{rdb}.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"关闭sync_redis连接池: {rdb}失败          ❌ \n Error:{str(e)}")
        logger.bind(name=None).success(
            f"*********  END:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} *********")

    @app.post("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()


def register_hook(app: FastAPI) -> None:
    """
    请求响应拦截 hook
    https://fastapi.tiangolo.com/tutorial/middleware/
    :param app:
    :return:
    """

    @app.middleware("http")
    async def logger_request(request: Request, call_next) -> Response:
        response = await call_next(request)
        return response


def register_exception(app: FastAPI) -> None:
    """
    全局异常捕获
    注意 别手误多敲一个s
    exception_handler
    exception_handlers
    两者有区别
        如果只捕获一个异常 启动会报错
        @exception_handlers(UserNotFound)
    TypeError: 'dict' object is not callable
    :param app:
    :return:
    """

    # 自定义异常 捕获
    @app.exception_handler(errors.TokenExpired)
    async def user_not_found_exception_handler(request: Request, exc: errors.TokenExpired):
        """
        token过期
        :param request:
        :param exc:
        :return:
        """
        log.info(
            f"token未知用户\nURL:{request.method}{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_4002(message=exc.err_desc)

    @app.exception_handler(errors.TokenAuthError)
    async def user_token_exception_handler(request: Request, exc: errors.TokenAuthError):
        """
        用户token异常
        :param request:
        :param exc:
        :return:
        """
        log.info(
            f"用户认证异常\nURL:{request.method}{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_4003(message=exc.err_desc)

    @app.exception_handler(errors.AuthenticationError)
    async def user_not_found_exception_handler(request: Request, exc: errors.AuthenticationError):
        """
        用户权限不足
        :param request:
        :param exc:
        :return:
        """
        log.info(f"用户权限不足 \nURL:{request.method}{request.url}")
        return response_code.resp_4003(message=exc.err_desc)

    @app.exception_handler(ValidationError)
    async def inner_validation_exception_handler(request: Request, exc: ValidationError):
        """
        内部参数验证异常
        :param request:
        :param exc:
        :return:
        """
        log.info(
            f"内部参数验证错误\nURL:{request.method}{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_5002(message=exc.errors())

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """
        log.info(
            f"请求参数格式错误\nURL:{request.method}{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_4001(message=exc.errors())

    # 捕获全部异常
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        全局所有异常
        :param request:
        :param exc:
        :return:
        """
        log.info(f"全局异常\n{request.method}URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_500()
