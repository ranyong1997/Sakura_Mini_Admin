#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:16
# @Author  : 冉勇
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @desc    : 总入口
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 跨域
from fastapi.responses import HTMLResponse  # 响应html
from loguru import logger
from back.app import settings
from back.app.database import Base, engine, get_db
from back.crud import services
from back.router.v1 import casbin_router, casbin_action_router, casbin_object_router, role_router, token_router, \
    user_token

app = FastAPI(
    title=settings.project_title,
    description=settings.project_description,
    version=settings.project_version,
    openapi_tags=settings.tags_metadata,
    license_info={
        "name": "开源MIT协议",
        "url": "https://opensource.org/licenses/MIT",
    },

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
app.include_router(casbin_router.router)
app.include_router(casbin_object_router.router)
app.include_router(casbin_router.router)
app.include_router(casbin_action_router.router)
app.include_router(role_router.router)
app.include_router(token_router.router)
app.include_router(user_token.router)

# 静态资源
# app.mount("/dist", StaticFiles(directory=os.path.join(BASE_DIR, 'dist')), name="dist")
# app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, 'dist/assets')), name="assets")


# 在数据库中生成表结构
Base.metadata.create_all(bind=engine)
# 生成初始化数据，添加了一个超级管理员并赋予所有管理权限，以及一些虚拟的用户。
services.create_data(next(get_db()))


# @app.get("/")
# def main():
#     html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'index.html')
#     with open(html_path, encoding="utf-8") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)


@app.on_event("startup")
async def startup_event():
    logger.info(f'{settings.BANNER}')
    logger.info(
        f"{settings.project_title} 正在运行环境: 【环境】 接口文档: http://{settings.server_host}:{settings.server_port}/docs")

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload_dirs=['back'],  # reload_dirs=['back'],仅检测back目录下的代码改动
        reload=True)
