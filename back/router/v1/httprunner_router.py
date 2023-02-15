#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 15:50
# @Author  : 冉勇
# @Site    : 
# @File    : httprunner_router.py
# @Software: PyCharm
# @desc    : HttpRunner路由
import json
import os
import traceback
import sys
import functools
from fastapi import APIRouter, Depends
from har2case.core import HarParser
from httprunner.cli import main_run
from pydantic import BaseSettings
from back.utils.httprunner_request import HttpRequest
from back.utils.logger import log

sys.path.append('../../../')
router = APIRouter(
    prefix="/v1",
    tags=["HttpRunner"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


class Settings(BaseSettings):
    ROOT_PATH: str = os.path.abspath("../hrun_proj")
    LOG_LEVEL: str = "DEBUG"
    EXCUTE_ARGS: list = ["-sW", "ignore:Module already imported:pytest.PytestWarning", "--save-tests"]


@functools.lru_cache()
def settings():
    return Settings()


# TODO:BUG:无法自动将har文件转换到testcase目录下
# @router.post("/run_har2case")
# async def run_har2case(har_path: str, config: Settings = Depends(settings)):
#     log.info(f"run_har2case.params: {har_path}")
#     resp = {
#         "code": 200,
#         "message": "success",
#         "results": {}
#     }
#     try:
#         har_path = os.path.join(config.ROOT_PATH, har_path)
#         log.debug(f"获取转换har文件地址:{har_path}")
#         if os.path.exists(har_path):
#             case_info = HarParser(har_path)._make_testcase("V2")
#             result = {"case_info": case_info, "har_path": har_path}
#             resp["results"] = result
#         else:
#             resp["code"] = 400
#             resp["message"] = f"Path Not Exist:{har_path}"
#     except Exception:
#         resp["code"] = 500
#         resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
#     log.debug("run_har2case.return:" + resp["message"])
#     return resp

@router.post("/run_online_debug")
async def run_online_debug(testcase_infos: dict):
    resp = {
        "code": 200,
        "message": "success",
        "results": {}
    }
    try:
        request_info = testcase_infos.get("teststeps")[0].get("request")
        method = request_info.get("method")
        url = request_info.get("url")
        kwargs = {}
        if request_info.get("headers"):
            kwargs['headers'] = request_info.get("headers")
        if request_info.get("cookies"):
            kwargs['cookies'] = request_info.get("cookies")
        if request_info.get("data"):
            kwargs['data'] = request_info.get("data")
        if request_info.get("json"):
            kwargs['json'] = request_info.get("json")
        if request_info.get("params"):
            kwargs['params'] = request_info.get("params")
        if request_info.get("upload"):
            kwargs['files'] = request_info.get("upload")
        req_resp = HttpRequest().request(method, url, **kwargs)
        resp["results"] = req_resp
    except Exception:
        resp["code"] = 500
        resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
    log.debug(resp["message"])
    return resp


@router.post("/run_pytest")
async def run_pytest(case_path: str, config: Settings = Depends(settings)):
    log.debug(f"run_pytest.params: {case_path}")
    resp = {
        "code": 200,
        "message": "success",
        "results": {}
    }
    try:
        testcase_json_path = os.path.join(config.ROOT_PATH, case_path)
        if os.path.exists(testcase_json_path):
            excute_args = config.EXCUTE_ARGS
            excute_args.append(testcase_json_path)
            exit_code = main_run(excute_args)
            summary_path = os.path.join(config.ROOT_PATH, "logs", f"{case_path.split('.')[0]}.summary.json")
            with open(summary_path, "r") as summary_file:
                summary = json.load(summary_file)
            if exit_code != 0:
                error_path = os.path.join("logs", "httprunner.exceptions.log")
                if os.path.exists(error_path):
                    with open(error_path, "r") as error_file:
                        message = error_file.read()
                    os.remove(error_path)
                else:
                    message = "httprunner.exceptions: Unexpected Error"
                resp["code"] = 300
                resp["message"] = message
            result = {"summary": summary, "case_path": case_path}
            resp["results"] = result
        else:
            resp["code"] = 400
            resp["message"] = f"Path Not Exist:{testcase_json_path}"
    except Exception:
        resp["code"] = 500
        resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
    log.debug("run_pytest.return: " + resp["message"])
    return resp
