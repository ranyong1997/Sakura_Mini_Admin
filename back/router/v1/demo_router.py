#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/30 19:29
# @Author  : 冉勇
# @Site    : 
# @File    : demo_router.py
# @Software: PyCharm
# @desc    :
from fastapi import Request, Form, APIRouter
from httprunner import HttpRunner, Config, Step, RunRequest
import json
from typing import List, Union
router = APIRouter(
    prefix="/v1",
    tags=["Demo"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


# @router.post("/runhttprunner/")
# async def run_httprunner(request: Request, api_data: str = Form(...)):
#     """
#     POST方法，运行HttpRunner测试套件，api_data是要运行的测试数据
#     """
#     # 解析api_data
#     api_list = json.loads(api_data)
#
#     # 构造HttpRunner运行需要的Config配置信息
#     config_dict = {
#         "config": {
#             "name": "FastAPI and HttpRunner",
#             "base_url": api_list[0]['request']['base_url']
#         },
#         "teststeps": []
#     }
#
#     for api in api_list:
#         # 构造HttpRunner运行需要的Step信息
#         step = Step(
#             name=api['name'],
#             request=RunRequest(
#                 url=api['request']['url'],
#                 method=api['request']['method'],
#                 headers=api['request']['headers'],
#                 json=api['request'].get('json'),
#                 params=api['request'].get('params')
#             ),
#             extract=api.get('extract'),
#             validate=api.get('validate')
#         )
#         config_dict['teststeps'].append(step.__dict__)
#
#     # 运行HttpRunner测试套件
#     config = Config.from_dict(config_dict)
#
#     runner = HttpRunner(report_template="html")
#     runner.run(config)
#
#     # 返回测试报告
#     return runner.summary

@router.post("/test/")
async def run_test(data: Union[str, List[dict]] = Form(...)):
    """
    运行httprunner测试
    data：str格式或list格式，内容是yaml格式或dict格式的httprunner测试用例数据
    """
    if isinstance(data, str):
        data = [item for item in HttpRunner().load_yaml(data)]
    elif isinstance(data, list):
        data = [item if isinstance(item, dict) else item.__dict__ for item in data]
    else:
        raise ValueError("data参数格式错误")

    res = HttpRunner().run_tests(data)

    return res.summary


# [{'name': '登陆', 'request': {'base_url': 'http://127.0.0.1:8000', 'url': '/v1/login/', 'method': 'POST', 'headers': {'Content-Type': 'application/json'}, 'json': {'username': 'root', 'password': '123456'}}, 'validate': [{'eq': ['status_code', 200]}]}, {'name': '查询用户信息', 'request': {'base_url': 'http://127.0.0.1:8000', 'url': '/v1/user/me/', 'method': 'GET', 'headers': {'Authorization': 'Bearer token'}}}]