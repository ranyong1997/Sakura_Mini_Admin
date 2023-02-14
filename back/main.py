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
from fastapi.middleware.cors import CORSMiddleware  # 跨域
from fastapi.responses import HTMLResponse  # 响应html
from loguru import logger
from back.app import settings
from back.app.database import Base, engine, get_db
from back.crud import services
from back.router.v1 import api_v1_router
from back.utils.redis import redis_client

app = FastAPI(
    title=settings.project_title,
    description=settings.project_description,
    version=settings.project_version,
    openapi_tags=settings.tags_metadata,
    license_info={
        "name": "开源MIT协议",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# 配置允许域名列表、允许方式、请求头、cookie等等
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers
)

# 挂载路由
app.include_router(
    api_v1_router
)


# 静态资源
# app.mount("/dist", StaticFiles(directory=os.path.join(BASE_DIR, 'dist')), name="dist")
# app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, 'dist/assets')), name="assets")


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
        services.create_data(next(get_db()))
        logger.bind(name=None).success("生成初始化数据成功.          ✔")
    except Exception as e:
        logger.bind(name=None).error(f"生成初始化数据失败.          ❌ \n Error:{str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    if settings.REDIS_OPEN:
        # 关闭redis连接
        await redis_client.close()


# @app.get("/")
# def main():
#     html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'index.html')
#     with open(html_path, encoding="utf-8") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload_dirs=['back'],  # reload_dirs=['back'],仅检测back目录下的代码改动
        reload=True)
