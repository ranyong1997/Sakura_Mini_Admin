#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:16
# @Author  : 冉勇
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @desc    : 总入口
import time
import traceback
import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from pydantic import ValidationError
from fastapi.responses import HTMLResponse  # 响应html
from loguru import logger
from back.app import settings
from back.dbdriver.mysql import Base, engine, get_db
from back.crud import user_services
from back.middleware import register_middleware
from back.router.v1 import api_v1_router, tags_metadata
from back.utils import response_code
from back.utils.core.init_scheduler import scheduler_init
from back.utils.exception import errors
from back.utils.logger import log
from back.dbdriver.redis import redis_client
from back.utils.registrar import register_router, register_init, register_hook, register_exception


def create_app() -> FastAPI:
    """
    生成Fastapi对象
    :return:
    """
    # 获取config下的debug调试,如果为True,可以调试docs,否则不可以调试
    if settings.DEBUG:
        app = FastAPI(
            title=settings.project_title,
            docs_url=settings.docs_url,
            redoc_url=settings.redoc_url,
            description=settings.project_description,
            version=settings.project_version,
            openapi_tags=tags_metadata,
            license_info={
                "name": "开源MIT协议",
                "url": "https://opensource.org/licenses/MIT",
            }
        )
    else:
        app = FastAPI(
            docs_url=None,
            redoc_url=None,
        )
    # 注册路由
    register_router(app)
    # 请求拦截
    register_hook(app)
    # 注册捕获全局异常
    register_exception(app)
    # 环境启动
    register_init(app)
    # 中间件
    register_middleware(app)
    return app

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
