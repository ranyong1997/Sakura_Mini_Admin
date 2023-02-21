#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/21 17:52
# @Author  : 冉勇
# @Site    : 
# @File    : response_schema.py
# @Software: PyCharm
# @desc    : 响应
from datetime import datetime
from typing import Optional, Any, Union, Set, Dict
from fastapi.encoders import jsonable_encoder
from pydantic import validate_arguments, BaseModel

_JsonEncoder = Union[Set[Union[int, str]], Dict[Union[int, str], Any]]

__all__ = [
    'ResponseModel',
    'response_base'
]


class ResponseModel(BaseModel):
    """
    统一返回模型, 可在 FastAPI 接口请求中指定 response_model 及更多操作
    """
    code: int = 200
    msg: str = 'Success'
    data: Optional[Any] = None

    class Config:
        json_encoders = {
            datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
        }


class ResponseBase:
    """
    响应Base
    """

    @staticmethod
    def __encode_json(data: Any):
        return jsonable_encoder(
            data,
            custom_encoder={
                datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    @staticmethod
    @validate_arguments
    def success(*, code: int = 200, msg: str = 'Success', data: Optional[Any] = None,
                exclude: Optional[_JsonEncoder] = None):
        """
        请求成功返回通用方法
        :param code: 返回状态码
        :param msg: 返回信息
        :param data: 返回数据
        :param exclude: 排除返回数据(data)字段, 见 Pydantic: https://shorturl.at/cjszF
        :return:
        """
        # 嵌套使用 pydantic dict() 方法的说明, 我想你需要了解.
        # 1. 为什么使用 pydantic dict() 方法执行 exclude ?
        # FastAPI 在最终返回结果前使用 jsonable_encoder() 进行序列化，具体方法为 get_request_handler(), 请在 fastapi 源码搜索查看;
        # 当前使用版本 fastapi <= 0.85.1 中的 jsonable_encoder() 行为方式和 pydantic dict() 方法并不完全相同,
        # jsonable_encoder() 中的 exclude 参数并不是支持任何形式 dict 结构深度排除, 就当前版本而言, 但当前版本 pydantic >= 1.10.2
        # 的 dict() 方法支持更友好的 exclude 参数形式, 包括深度排除;
        # 2. ResponseModel 中的 data 为什么还要调用 jsonable_encoder() ?
        # jsonable_encoder() 有一个非常好的参数 custom_encoder, 可以创建自己想要的解析器来解析数据, 比如 datetime, 这样就可以序列化
        # 我们想要的格式, 还有一点 SQLAlchemy 返回的是对象, 并不是字典, 利用 jsonable_encoder() 将 SQLAlchemy 对象解析为字典;
        # 3. 对于 data 使用 jsonable_encoder() 进行序列化是否有性能损耗 ?
        # 对于目前在 ResponseModel 中加持一层 jsonable_encoder() 方法解析 data 带来的性能损耗, 并未测试, 但性能丢失点与
        # jsonable_encoder() 方法解析 data 数据的速度相关联, 原因是 ResponseModel 在 fastapi 最终返回前同样会调用
        # jsonable_encoder() 方法解析数据, 如果是 pydantic 格式, 就会调用 pydantic dict() 方法, 再调用 jsonable_encoder()
        # 对 dict() 之后的数据进行解析, 这样看 ResponseModel.dict() 方法的调用只是提前发生了, 现在将直接传入 dict() 之后的数据给
        # jsonable_encoder() 方法, 所以 ResponseModel.dict() 方法总会执行一次, 而提前调用 dict() 方法, 再将数据传输到
        # jsonable_encoder() 方法这个过程中性能损耗可能与数据量大小相关;
        # 附加一个当前版本 fastapi 未合并, 但你可能感兴趣的 Pull requests 链接: https://github.com/tiangolo/fastapi/pull/5462
        # 3. 可以避免此性能损耗吗 ?
        # 为了数据灵活性和写起来舒服, 避免个锤子
        # 4. 额外说明
        # ResponseModel 可以检测数据类型, 返回前预知数据类型错误, 避免了返回之后才收到不符合数据类型的数据, 理论上是有益的, 但是你也可以
        # 看到现有的返回方法都加了 @validate_arguments 装饰器, 它也由 pydantic 提供, 数据类型检测比 ResponseModel 更提前, 所以
        # 可以放心去除 ResponseModel 返回格式, 直接使用 dict(code, msg, data) 格式. 请注意, 将 ResponseModel 返回格式做为统一返回
        # 样式很 nice, 其实还可以在接口装饰器参数中使用 response_model 相关配置来控制返回数据和深度排除等操作, 如果你喜欢这样做, 请注意
        # 查看 ResponseModel 类说明;
        data = data if data is None else ResponseBase.__encode_json(data)
        return ResponseModel(code=code, msg=msg, data=data).dict(exclude={'data': exclude})

    @staticmethod
    @validate_arguments
    def fail(*, code: int = 400, msg: str = 'Bad Request', data: Any = None, exclude: Optional[_JsonEncoder] = None):
        data = data if data is None else ResponseBase.__encode_json(data)
        return ResponseModel(code=code, msg=msg, data=data).dict(exclude={'data': exclude})

    @staticmethod
    @validate_arguments
    def response_200(*, msg: str = 'Success', data: Optional[Any] = None, exclude: Optional[_JsonEncoder] = None):
        data = data if data is None else ResponseBase.__encode_json(data)
        return ResponseModel(code=200, msg=msg, data=data).dict(exclude={'data': exclude})


response_base = ResponseBase()
