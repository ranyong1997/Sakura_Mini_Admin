#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:16
# @Author  : 冉勇
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @desc    : 总入口
import traceback
import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # 跨域
from fastapi.responses import HTMLResponse  # 响应html
from pydantic import ValidationError
from loguru import logger
from back.app import settings
from back.app.database import Base, engine, get_db
from back.crud import user_services
from back.router.v1 import api_v1_router
from back.utils import response_code
from back.utils.exception import errors
from back.utils.logger import log
from back.utils.redis import redis_client


def create_app() -> FastAPI:
    """
    生成Fastapi对象
    :return:
    """
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.project_title,
        description=settings.project_description,
        version=settings.project_version,
        openapi_tags=settings.tags_metadata,
        license_info={
            "name": "开源MIT协议",
            "url": "https://opensource.org/licenses/MIT",
        }
    )
    # 跨域设置
    register_cors(app)
    # 注册路由
    register_router(app)
    # 请求拦截
    register_hook(app)
    # 注册捕获全局异常
    register_exception(app)
    # 环境启动
    register_init(app)
    return app


def register_cors(app: FastAPI) -> None:
    """
    配置允许域名列表、允许方式、请求头、cookie等等
    :param app:
    :return:
    """
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.origins,
            allow_credentials=True,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers
        )


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
            logger.bind(name=None).success("数据库和表创建成功.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"数据库和表创建失败.          ❌ \n Error:{str(e)}")
            raise
        if settings.REDIS_OPEN:
            # 连接redis
            try:
                await redis_client.init_redis_connect()
                logger.bind(name=None).success("redis连接成功.          ✔")
            except Exception as e:
                logger.bind(name=None).error(f"redis连接失败.          ❌ \n Error:{str(e)}")
                raise
        try:
            # 生成初始化数据，添加了一个超级管理员并赋予所有管理权限，以及一些虚拟的用户。
            user_services.create_data(next(get_db()))
            logger.bind(name=None).success("生成初始化数据成功.          ✔")
        except Exception as e:
            logger.bind(name=None).error(f"生成初始化数据失败.          ❌ \n Error:{str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        if settings.REDIS_OPEN:
            # 关闭redis连接
            await redis_client.close()


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


# 静态资源
# app.mount("/dist", StaticFiles(directory=os.path.join(BASE_DIR, 'dist')), name="dist")
# app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, 'dist/assets')), name="assets")


# @app.get("/")
# def main():
#     html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'index.html')
#     with open(html_path, encoding="utf-8") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)

app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload_dirs=['back'],  # reload_dirs=['back'],仅检测back目录下的代码改动
        workers=4,
        reload=True)
