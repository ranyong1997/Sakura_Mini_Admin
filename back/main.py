#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 11:16
# @Author  : 冉勇
# @Site    : 
# @File    : main.py
# @Software: PyCharm
# @desc    :
import os
import sys
import uvicorn
from back.app import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 跨域
from fastapi.staticfiles import StaticFiles  # 设置静态目录
from fastapi.responses import HTMLResponse  # 响应html
from back.app.database import Base, engine

# 将当前目录添加到系统变量中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
# 组装数据库的绝对地址
DB_DIR = os.path.join(BASE_DIR, "miniadmin_data.db")

app = FastAPI(
    title=settings.project_title,
    description=settings.project_description,
    version=settings.project_version,
    terms_of_service="#",
    license_info={
        "name": "✶  🎀  GitHub地址  🎀  ✶",
        "url": "https://github.com/ranyong1997"
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

# 路由
# app.include_router()


# 静态资源
# app.mount("/dist", StaticFiles(directory=os.path.join(BASE_DIR, 'dist')), name="dist")
# app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, 'dist/assets')), name="assets")


# 在数据库中生成表结构
Base.metadata.create_all(bind=engine)


# 生成初始化数据，添加一个超级管理员并赋予所有管理权限，以及一些虚拟用户
@app.get("/")
def main():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'index.html')
    with open(html_path, encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.on_event("startup")
async def startup_event():
    print(f'{settings.BANNER}')
    print(f"{settings.project_title} 正在运行环境: 【环境】 网址: http://localhost:8000/docs")


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload_dirs=['back'],  # reload_dirs=['back'],仅检测back目录下的代码改动
        reload=True)
