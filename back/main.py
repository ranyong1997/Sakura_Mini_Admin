#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:16
# @Author  : 冉勇
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @desc    : 总入口
import uvicorn
from fastapi import FastAPI
from back.app import settings
from back.crud import user_services  # 删除会报错奇怪的bug
from back.middleware import register_middleware
from back.router.v1 import tags_metadata
from back.utils.registrar import register_router, register_init, register_hook, register_exception
from back.utils.static import static_registration


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
    # 静态资源
    static_registration(app)

    return app


app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload_dirs=['back'],  # reload_dirs=['back'],仅检测back目录下的代码改动
        workers=4,
        reload=True,
        log_config=None)
