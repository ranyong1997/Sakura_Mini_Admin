#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/1 21:47
# @Author  : 冉勇
# @Site    : 
# @File    : lark_test_report.py
# @Software: PyCharm
# @desc    :
import json
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
                            "content": "**🗳 任务**: ${job_name} ",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**📍类型**: ${job_type}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**💃 执行人**: ${execute_by}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🍕 测试通过率**: ${pass_rate}",
                            "tag": "lark_md"
                        }
                    }, {
                        "is_short": False,
                        "text": {
                            "content": "**🍔 执行通过率(忽略跳过)**: ${pass_rate_ignore_skipped}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🍤 执行用例数**: ${cases}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🌭 执行步骤数**: ${steps}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🍜 通过/失败/错误/跳过**: ${successes}/${failures}/${errors}/${skipped}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🍣 执行线程数**: ${threads}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**⏰ 执行耗时**: ${duration}(s)",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**⏰ 开始时间**: ${start_at}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🍥 任务状态**: ${status}",
                            "tag": "lark_md"
                        }
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "**🔥 异常信息**: ${exception}",
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
                            "content": "查看报告",
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
                "content": "📮 自动化测试报告",
                "tag": "plain_text"
            }
        }
    }}

response = requests.request("POST", url, headers=headers, json=AUTOTEST_LARK_MESSAGE_TEMPLATE)

print(response.text)


# https://blog.csdn.net/sumeixiaoxiao/article/details/128022326