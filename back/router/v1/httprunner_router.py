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
import subprocess
import traceback
import functools
from fastapi import APIRouter, Depends
from har2case.core import HarParser
from pydantic import BaseSettings
from back.schemas import httprunner_schemas
from back.utils.httprunner_client import HttpClient
from back.utils.logger import log

router = APIRouter(
    prefix="/v1",
    tags=["HttpRunner"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


class Settings(BaseSettings):
    ROOT_PATH: str = os.path.abspath("../hrun_proj")
    LOG_LEVEL: str = "DEBUG"
    HRUN_EXCUTE_ARGS: list = ["hrun", "-sW", "ignore:Module already imported:pytest.PytestWarning", "--save-tests",
                              "--log-level", LOG_LEVEL]


@functools.lru_cache()
def settings():
    return Settings()


@router.post("/run_har2case")
async def run_har2case(har_path: str, config: Settings = Depends(settings)):
    """
    将*.har转为json文件
    """
    log.info(f"run_har2case.params: {har_path}")
    resp = {
        "code": 200,
        "message": "success",
        "results": {}
    }
    try:
        har_path = os.path.join(config.ROOT_PATH, har_path)
        log.debug(f"获取转换har文件地址:{har_path}")
        if os.path.exists(har_path):
            # 将*.har转*.json的内容
            case_info = HarParser(har_path)._make_testcase("V2")
            resp["results"] = {"case_info": case_info, "har_path": har_path}
        else:
            resp["code"] = 400
            resp["message"] = f"Path Not Exist:{har_path}"
    except Exception:
        resp["code"] = 500
        resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
    log.debug("run_har2case.return:" + resp["message"])
    return resp


@router.post("/run_debug")
async def run_debug(case_info: dict):
    """
    将har转的json内容复制到这，可以debug调试
    """
    resp = {
        "code": 200,
        "message": "success",
        "results": {}
    }
    try:
        request_info = case_info.get("teststeps")[0].get("request")
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
        hc = HttpClient()
        req_resp = hc.request(method, url, **kwargs)
        hc.log()
        resp["results"] = req_resp
    except Exception:
        resp["code"] = 500
        resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
    log.debug(resp["message"])
    return resp


@router.post("/run_subprocess")
async def run_subprocess(testcase_info: httprunner_schemas.HttpRunner_rule, config: Settings = Depends(settings)):
    """
    run测试用例
    """
    log.info(f"run_subprocess.params: {testcase_info}")
    resp = {
        "code": 200,
        "message": "success",
        "results": {}
    }
    try:
        case_path = testcase_info.case_path
        testcase_json_path = os.path.join(config.ROOT_PATH, case_path)
        print(testcase_json_path)
        if os.path.exists(testcase_json_path):
            excute_args = []
            excute_args.extend(config.HRUN_EXCUTE_ARGS)
            excute_args.append(testcase_json_path)
            CompletedProcess = subprocess.run(excute_args)
            summary_path = os.path.join(config.ROOT_PATH, "logs", f"{case_path.split('.')[0]}.summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, "r") as summary_file:
                    summary = json.load(summary_file)
                resp["results"] = {"summary": summary, "caseID": testcase_info.caseId, "case_path": case_path}
                os.remove(summary_path)
                if CompletedProcess.returncode != 0:
                    error_path = os.path.join("logs", "httprunner.exceptions.log")
                    if os.path.exists(error_path):
                        with open(error_path, "r") as error_file:
                            message = error_file.read()
                        os.remove(error_path)
                    else:
                        message = "httprunner.exceptions: Unexpected Error"
                    resp["code"] = 300
                    resp["message"] = message
            else:
                resp["code"] = 400
                resp["message"] = f"Summary Not Generated:{summary_path}"
        else:
            resp["code"] = 400
            resp["message"] = f"Path Not Exist:{testcase_json_path}"
    except Exception:
        resp["code"] = 500
        resp["message"] = f"Unexpected Error:{traceback.format_exc()}"
    log.info("run_subprocess.return: " + resp["message"])
    return resp
