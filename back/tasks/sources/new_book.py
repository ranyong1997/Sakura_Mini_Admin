#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/13 18:30
# @Author  : 冉勇
# @Site    : 
# @File    : new_book.py
# @Software: PyCharm
# @desc    :
import re
import traceback
import aiohttp
from datetime import datetime, timedelta
from back.tasks.sources import USER_AGENTS
from selectolax.parser import HTMLParser
import random
from back.basesever.service import SyncMysqlBaseService
from back.utils.core.init_scheduler import scheduler
from back.utils.logger import log


class NewBook:

    def __init__(self):
        self._DOUBAN = 'https://book.douban.com'
        self._Base_Url = "https://book.douban.com/latest?subcat=全部&p={page}"
        self._proxies = {}
        self._headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://book.douban.com/',
            'User-Agent': random.choice(USER_AGENTS),
        }
        self.mysql = SyncMysqlBaseService()

    async def get_search_list(self):
        url = self._Base_Url.format(page='1')
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers, proxy=self._proxies, timeout=10) as resp:
                content = await resp.read()
                tree = HTMLParser(content)
                tags = tree.css_first('div[class="paginator"]')
                tags = tags.text(strip=True, separator=" ")
                sd = re.findall(r"(\d+)", tags)
                return int(sd[-1])

    async def get_new_book_info(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers, timeout=10) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    tree = HTMLParser(content)
                    ul = tree.css_first('ul[class="chart-dashed-list"]')
                    res_list = []
                    for li in ul.css("li"):
                        res = dict()
                        res['image_url'] = li.css_first('div[class="media__img"]').css_first('img').attrs.get('src')
                        info = li.css_first('div[class="media__body"]')
                        res['title'] = info.css_first('h2[class="clearfix"] a').text(strip=True)
                        other_info = info.css_first('p[class="subject-abstract color-gray"]').text(strip=True)
                        date_ = re.findall(
                            '(\d{4}-\d{1,2}-\d{1,2}|\d{4}-\d{1,2}|\d{4}年\d{1,2}月|\d{4}年\d{1,2}月\d{1,2}日|\d{4}\\\d{1,2}\\\d{1,2}|\d{4}\\\d{1,2})',
                            other_info)
                        res['public_date'] = date_[0] if date_ else ''
                        res['author'] = other_info.split('/')[0]
                        res_list.append(res)

                    return res_list

    async def run(self):
        data_len = await self.get_search_list()
        for va in range(1, data_len + 1):
            url = self._Base_Url.format(page=va)
            book_info = await self.get_new_book_info(url)
            print(book_info)
            self.save_db(book_info)
        log.info("目前有新书")
        return True

    def save_db(self, data):
        self.mysql.insert_or_update(table_name='cw_book', values=data,
                                    update_name=['image_url'])


async def start_book():
    try:
        await NewBook().run()
    except Exception as e:
        log.error(traceback.format_exc(e))
    finally:
        try:
            next_time = datetime.now() + timedelta(hours=random.randint(10, 24))
            scheduler.reschedule_job(job_id='new_book', trigger='interval', start_date=next_time, days=2)
            log.info(f'修改爬取数据信息定时任务 下次执行时间为：{next_time}')
        except Exception as e:
            log.exception(f"修改 book 定时任务失败： {traceback.format_exc(e)}")
