#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/24 11:47
# @Author  : 冉勇
# @Site    : 
# @File    : send_email.py
# @Software: PyCharm
# @desc    : 发送邮件重置密码功能
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from back.app import settings
from back.app.config import Config
from back.utils.generate_string import get_uuid
from back.utils.logger import log

_only_one = get_uuid()

# todo:采用nijia2进行构建模板发文
SEND_RESET_PASSWORD_TEXT = f'您的重置密码验证码为：{_only_one}\n为了不影响您正常使用，' \
                           f'请在{int(settings.COOKIES_MAX_AGE / 60)}分钟内完成密码重置'


def send_verification_code_email(to: str, code: str, text: str = SEND_RESET_PASSWORD_TEXT):
    """
    发送验证码电子邮件

    :param to: 收件人
    :param code: 验证码
    :param text: 邮件文本内容
    :return:
    """
    _text = text.replace(_only_one, code)
    message = MIMEMultipart()
    message['subject'] = Config.EMAIL_DESCRIPTION
    message['from'] = Config.EMAIL_USER
    message.attach(MIMEText(_text, _charset="utf-8"))
    # 登录smtp服务器并发送邮件
    try:
        if Config.EMAIL_SSL:
            smtp = smtplib.SMTP_SSL(host=Config.EMAIL_SERVER, port=Config.EMAIL_PORT)
        else:
            smtp = smtplib.SMTP(host=Config.EMAIL_HOST, port=Config.EMAIL_PORT)
        smtp.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
        smtp.sendmail(message['from'], to, message.as_string())
        smtp.quit()
    except Exception as e:
        log.error('邮件发送失败 {}', e)
        raise Exception('邮件发送失败') from e
