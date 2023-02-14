#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 16:04
# @Author  : 冉勇
# @Site    : 
# @File    : httprunner_request.py
# @Software: PyCharm
# @desc    :
import json
import logging

import requests
from requests import Request, Response
from requests.exceptions import (
    InvalidSchema, InvalidURL, MissingSchema, RequestException
)

from back.utils.logger import log


class HttpRequest(requests.Session):
    def request(self, method: str, url: str, **kwargs: dict) -> dict:
        ex_msg = ''
        try:
            resp_obj = requests.Session.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL, RequestException) as ex:
            ex_msg = str(ex)
            resp_obj = Response()
            resp_obj.request = Request(method, url).prepare()
        request_headers = dict(resp_obj.request.headers)
        request_cookies = resp_obj.request._cookies.get_dict()
        request_body = resp_obj.request.body
        if request_body is not None:
            try:
                request_body = json.loads(request_body)
            except:
                pass
            request_content_type = {key.lower(): value for key, value in request_headers.items()}.get('content-type')
            if request_content_type and 'multipart/form-data' in request_content_type:
                request_body = 'upload file stream (OMITTED)'
        request_data = {
            'method': resp_obj.request.method,
            'url': resp_obj.request.url,
            'headers': request_headers,
            'cookies': request_cookies,
            'body': request_body
        }
        resp_headers = dict(resp_obj.headers)
        lower_resp_headers = {key.lower(): value for key, value in resp_headers.items()}
        content_type = lower_resp_headers.get('content-type', '')

        if 'image' in content_type:
            response_body = resp_obj.content
        else:
            if not resp_obj.status_code:
                response_body = ex_msg
            else:
                try:
                    response_body = resp_obj.json()
                except ValueError:
                    response_body = resp_obj.text
                    print('response_body', response_body, type(response_body), resp_obj.status_code)
                    if not isinstance(response_body, (str, bytes)):
                        response_body = response_body
                    if len(response_body) > 512:
                        omitted_body = response_body[0:512]
                        appendix_str = f" ... OMITTED {len(response_body) - 512} CHARACTORS ..."
                        if isinstance(response_body, bytes):
                            appendix_str = appendix_str.encode("utf-8")
                        response_body = omitted_body + appendix_str
        response_data = {
            "status_code": resp_obj.status_code,
            "cookies": resp_obj.cookies or {},
            "encoding": resp_obj.encoding,
            "headers": resp_headers,
            "content_type": content_type,
            "body": response_body
        }
        req_resp = {'request': request_data, 'response': response_data}
        request_info = f"\nrequest info:\n> {method} {url}\n> kwargs: {json.dumps(kwargs, indent=4, ensure_ascii=False)}"
        for r_type in req_resp:
            msg = f"\n================== {r_type} details ==================\n"
            for key, value in req_resp[r_type].items():
                if isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value, indent=4, ensure_ascii=False)
                msg += f"{key:<8} : {value}\n"
            request_info += msg
        log.debug(request_info)
        return req_resp


if __name__ == '__main__':
    method = "GET"
    headers = {"user-agent": "Edg/106.0.1370.47", 'Content-Type': 'application/json;charset=UTF-8'}
    url = 'https://api.wrdan.com/shorturl'
    data = ''
    jsons = ''
    params = {"url": "https://api.wrdan.com", "api": "mrwso"}
    print(HttpRequest().request(method=method, url=url, headers=headers, params=params))
