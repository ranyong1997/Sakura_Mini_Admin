#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/1 21:47
# @Author  : εε
# @Site    : 
# @File    : lark_test_report.py
# @Software: PyCharm
# @desc    :
import requests

url = "https://open.feishu.cn/open-apis/bot/v2/hook/fce32975-4d2f-49ab-b7a0-72921b173bb9"

headers = {
    'Content-Type': 'application/json'
}

AUTOTEST_LARK_MESSAGE_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "config": {
            "wide_screen_mode": True
        },
        "elements": [
            {
                "fields": [
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π³ δ»»ε‘**: ${job_name} ",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**πη±»ε**: ${job_type}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π ζ§θ‘δΊΊ**: ${execute_by}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π ζ΅θ―ιθΏη**: ${pass_rate}",
                            "tag": "lark_md"
                        }
                    }, {
                        "is_short": False,
                        "text": {
                            "content": "**π ζ§θ‘ιθΏη(εΏ½η₯θ·³θΏ)**: ${pass_rate_ignore_skipped}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π€ ζ§θ‘η¨δΎζ°**: ${cases}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π­ ζ§θ‘ζ­₯ιͺ€ζ°**: ${steps}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π ιθΏ/ε€±θ΄₯/ιθ――/θ·³θΏ**: ${successes}/${failures}/${errors}/${skipped}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π£ ζ§θ‘ηΊΏη¨ζ°**: ${threads}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**β° ζ§θ‘θζΆ**: ${duration}(s)",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**β° εΌε§ζΆι΄**: ${start_at}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π₯ δ»»ε‘ηΆζ**: ${status}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**π₯ εΌεΈΈδΏ‘ζ―**: ${exception}",
                            "tag": "lark_md"
                        }
                    },
                ],
                "tag": "div"
            },
            {
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "ζ₯ηζ₯ε",
                            "tag": "plain_text"
                        },
                        "type": "primary",
                        "url": "${report_address}"
                    }
                ],
                "tag": "action"
            }
        ],
        "header": {
            "template": "purple",
            "title": {
                "content": "π? θͺε¨εζ΅θ―ζ₯ε",
                "tag": "plain_text"
            }
        }
    }}

response = requests.request("POST", url, headers=headers, json=AUTOTEST_LARK_MESSAGE_TEMPLATE)

print(response.text)
