import json
import requests
from requests import Request, Response
from back.utils.logger import log
from requests.exceptions import (
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    RequestException,
)


class HttpClient(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        self.method = None
        self.url = None
        self.kwargs = None
        self.req_resp = None
        self.ex_msg = None

    def request(self, method: str, url: str, **kwargs: dict) -> dict:
        self.method = method
        self.url = url
        self.kwargs = kwargs
        try:
            resp_obj = requests.Session.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL, RequestException) as ex:
            self.ex_msg = str(ex)
            resp_obj = Response()
            resp_obj.request = Request(method, url).prepare()

        # record actual request info
        request_headers = dict(resp_obj.request.headers)
        request_cookies = resp_obj.request._cookies.get_dict()
        request_body = resp_obj.request.body
        if request_body is not None:
            try:
                request_body = json.loads(request_body)
            except:
                pass
            request_content_type = {key.lower(): value for key, value in request_headers.items()}.get("content-type")
            if request_content_type and "multipart/form-data" in request_content_type:
                request_body = "upload file stream (OMITTED)"
        request_data = {
            "method": resp_obj.request.method,
            "url": resp_obj.request.url,
            "headers": request_headers,
            # "cookies":request_cookies,
            "body": request_body
        }

        # record response info
        resp_headers = dict(resp_obj.headers)
        response_content_type = {key.lower(): value for key, value in resp_headers.items()}.get("content-type", "")
        if "image" in response_content_type:
            response_body = resp_obj.content
        else:
            if not resp_obj.status_code:
                response_body = self.ex_msg
            else:
                try:
                    response_body = resp_obj.json()
                except ValueError:
                    response_body = resp_obj.text
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
            "resp_time(s)": resp_obj.elapsed.total_seconds(),
            "cookies": resp_obj.cookies.get_dict() or {},
            "encoding": resp_obj.encoding,
            "content_type": response_content_type,
            "body": response_body
        }

        self.req_resp = {"request": request_data, "response": response_data}

        return self.req_resp

    def log(self) -> None:
        request_info = f"\nrequest info:\n> {self.method} {self.url}\n> kwargs: {json.dumps(self.kwargs, indent=4, ensure_ascii=False)}"
        for r_type in self.req_resp:
            msg = f"\n================== {r_type} details ==================\n"
            for key, value in self.req_resp[r_type].items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, indent=4, ensure_ascii=False)
                msg += f"{key:<12} : {value}\n"
            request_info += msg
        log.debug(request_info)
