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
from datetime import datetime, timedelta
from . import USER_AGENTS
from selectolax.parser import HTMLParser
import httpx
import random
from loguru import logger
from back.basesever.service import SyncMysqlBaseService
from back.utils.core.init_scheduler import scheduler


class NewBook:

    def __init__(self):
        self._DOUBAN = 'https://book.douban.com'
        self._Base_Url = "https://book.douban.com/latest?subcat=全部&p={page}"
        self._proxies = {}
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://book.douban.com/',
            'User-Agent': random.choice(USER_AGENTS),
            # 'Cookie': 'bid=nkRqb7w14xQ; douban-fav-remind=1; ll="118172"; push_noty_num=0; push_doumail_num=0; gr_user_id=86cb43aa-aaff-4fd0-917b-36a1336a10a5; ct=y; Hm_lvt_16a14f3002af32bf3a75dfe352478639=1642583683; dbcl2="253159781:p4VXUjbgx4k"; ck=43IV; ap_v=0,6.0; _pk_ref.100001.4cf6=["","",1643079468,"https://www.douban.com/"]; _pk_ses.100001.4cf6=*; _pk_id.100001.4cf6=b480c755a678daec.1642487039.7.1643079471.1643019875.',  # 浏览器登录后复制Cookie贴到此处
        }
        self.mysql = SyncMysqlBaseService()

    def get_search_list(self):
        url = self._Base_Url.format(page='1')
        req = httpx.get(url, headers=self._headers, proxies=self._proxies, timeout=10)
        tree = HTMLParser(req.content)
        tags = tree.css_first('div[class="paginator"]')
        tags = tags.text(strip=True, separator=" ")
        sd = re.findall(r"(\d+)", tags)
        return int(sd[-1])

    def get_new_book_info(self, url: str):
        req = httpx.get(url, headers=self._headers, timeout=10)
        if req.status_code == 200:
            tree = HTMLParser(req.content)
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

    def run(self):
        data_len = self.get_search_list()
        for va in range(1, data_len + 1):
            url = self._Base_Url.format(page=va)
            book_info = self.get_new_book_info(url)
            # print(book_info)
            # self.save_db(book_info)
        logger.info("目前有新书")
        return True

    def save_db(self, data):
        self.mysql.insert_or_update(table_name='cw_book', values=data,
                                    update_name=['image_url'])


def start_book():
    try:
        NewBook().run()
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        try:
            next_time = datetime.now() + timedelta(hours=random.randint(10, 24))
            scheduler.reschedule_job(job_id='new_book', trigger='interval', start_date=next_time, days=2)
            logger.info(f'修改爬取数据信息定时任务 下次执行时间为：{next_time}')
        except Exception as e:
            logger.exception(f"修改 book 定时任务失败： {traceback.format_exc()}")
