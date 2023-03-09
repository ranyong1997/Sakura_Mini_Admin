#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/20 17:11
# @Author  : 冉勇
# @Site    : 
# @File    : captcha_router.py
# @Software: PyCharm
# @desc    : 图片验证码
from fast_captcha import img_captcha
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse
from back.app import settings
from back.utils.generate_string import get_uuid
from back.dbdriver.redis import redis_client

router = APIRouter(
    prefix="/v1",
    tags=["验证码"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get('/captcha', summary='获取验证码')
async def get_ca(request: Request):
    """
    生成验证码图片
    """
    img, code = img_captcha()
    uid = get_uuid()
    request.app.state.captcha_uid = uid
    # 将验证码写入redis,并设置过期销毁时间,创建根目录/Sakura/captcha
    await redis_client.set(f'{settings.REDIS_PREFIX}:captcha:{uid}', code,
                           ex=settings.CAPTCHA_EXPIRATION_TIME)
    return StreamingResponse(content=img, media_type='image/jpeg')


@router.get('/captcha/test', summary='验证码验证')
async def check_captcha(request: Request):
    """
    验证码验证
    """
    try:
        code = request.app.state.captcha_uid
        return {'code': 200, 'captcha_uid': code}
    except AttributeError:
        return {'msg': '请先获取验证码'}
