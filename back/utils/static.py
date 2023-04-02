#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/21 15:39
# @Author  : 冉勇
# @Site    : 
# @File    : static.py
# @Software: PyCharm
# @desc    :
import os
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from back.app.config import base_dir


def static_registration(app: FastAPI()) -> None:
    """静态资源注册"""

    app.mount("/static", StaticFiles(directory="back/static"), name="static")

    @app.get("/")
    def main():
        html_path = os.path.join(base_dir, 'static/dist', 'index.html')
        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
