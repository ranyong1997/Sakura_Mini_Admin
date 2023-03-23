#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:39
# @Author  : 冉勇
# @Site    : 
# @File    : mysql_.py
# @Software: PyCharm
# @desc    : 异步mysql连接
import aiomysql
import traceback
import pymysql
from typing import Union, Tuple, Dict
from dbutils.pooled_db import PooledDB
from back import environment
from back.schemas.response_schemas import HttpException
from back.utils.exception.errors import SQL_ERROR
from back.utils.logger import log


class AioMysqlDb:
    # 生成异步的
    def __init__(self, **kwargs):
        self.pool = None
        self.maxsize = kwargs.get("maxsize") or 5
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.user = kwargs.get("user")
        self.password = kwargs.get("pwd")
        self.db = kwargs.get("db")
        self.__transaction = dict()
        self.__transaction_cur = dict()
        self.__transaction_begin = dict()

    async def connect_pool(self):
        """设置mysql连接池"""
        if not self.host:
            return
        log.info(f"连接异步数据库:{self.host}, -- {self.db}")
        self.pool = await aiomysql.create_pool(
            minsize=3,
            maxsize=self.maxsize,
            host=self.host,
            port=self.port,
            user=self.user,
            pool_recycle=3600,
            password=self.password,
            db=self.db,
            autocommit=False,
            connect_timeout=10,
            charset="utf8mb4"
        )

    async def select(self, sql: str, data: Union[dict, list] = None,
                     many: bool = True, t_index: str = None) -> Union[Dict, Tuple]:
        """
        数据库选择操作
            :param sql: 待执行的SQL语句
            :param data: 参数部分
            :param many: 是否返回所有数据，否则只返回第一条
            :param t_index: 事物句柄
        """
        log_sql = sql.replace("\n", ' ')
        log.info(f'select sql: {log_sql}; data: {data}; t_index: {t_index}')
        if t_index:
            cursor = self.__transaction_cur[t_index]
            return await self.__many_or_one_select(cursor, sql, data=data, many=many)

        else:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    rows = await self.__many_or_one_select(cursor, sql, data=data, many=many)
                    await conn.commit()
                    return rows

    async def __many_or_one_select(self, cursor: Union[aiomysql.cursors.Cursor, aiomysql.cursors.DictCursor],
                                   sql: str, data: Union[dict, list] = None, many: bool = True):
        """
        数据库查询操作,由 select  操作调用
        :param cursor: 数据库链接游标
        :param sql: 待执行的SQL语句
        :param data: 参数部分
        :param many: 是否返回所有数据，否则只返回第一条
        """
        await cursor.execute(sql, data)
        if many:
            data = await cursor.fetchall()
        else:
            data = await cursor.fetchone()
        if not data:
            data = [] if many else {}
        return data

    async def execute(self, sql: str, data: Union[dict, list] = None, t_index: str = None) -> bool:
        """
        数据库选择操作
            :param sql: 待执行的SQL语句
            :param data: 参数部分
            :param t_index: 事物句柄
        """
        log_sql = sql.replace("\n", ' ')
        log.info(f'execute: {log_sql}; data: {data}; t_index: {t_index}')
        if t_index:
            trans_cur = self.__transaction_cur[t_index]
            try:
                await trans_cur.execute(sql, data)
            except Exception as error:
                log.error(f"sql error ：{log_sql} ； data: {data} ;\n error：{error}")
                await self.rollback(t_index)
                raise HttpException(code=SQL_ERROR)
            return True
        else:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    try:
                        await cursor.execute(sql, data)
                        await conn.commit()
                    except Exception as error:
                        log.error(f"sql error ：{log_sql} ； data: {data} ;\n error：{error}")
                        await conn.rollback()
                        raise HttpException(code=SQL_ERROR)
                    return True

    async def executemany(self, sql: str, data: Union[dict, list] = None, t_index: str = None) -> bool:
        """
        数据库选择操作
            :param sql: 待执行的SQL语句
            :param data: 参数部分
            :param t_index: 事物句柄
        """
        log_sql = sql.replace("\n", ' ')
        log.info(f'execute: {log_sql}; data: {data}; t_index: {t_index}')
        if t_index:
            trans_cur = self.__transaction_cur[t_index]
            try:
                await trans_cur.executemany(sql, data)
            except Exception as error:
                log.error(f"sql error ：{log_sql} ； data: {data} ;\n error：{error}")
                await self.rollback(t_index)
                raise HttpException(code=SQL_ERROR)
            return True
        else:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    try:
                        await cursor.executemany(sql, data)
                        await conn.commit()
                    except Exception as error:
                        log.error(f"sql error ：{log_sql} ； data: {data} ;\n error：{error}")
                        await conn.rollback()
                        raise HttpException(code=SQL_ERROR)
                    return True

    async def get_connect(self):
        return await self.pool.acquire()

    async def begin(self, t_index: str = None, dictcursor: bool = True) -> str:
        """
        transation begin
        :param t_index: 事务句柄
        :param dictcursor: 需要的游标类型
        :return:
        """
        trans_conn = await self.get_connect()
        if not t_index:
            t_index = str(trans_conn.__hash__())
        self.__transaction[t_index] = trans_conn
        cur_type = aiomysql.DictCursor if dictcursor else aiomysql.Cursor
        self.__transaction_cur[t_index] = await self.__transaction[t_index].cursor(cur_type)
        return t_index

    async def commit(self, t_index: str) -> bool:
        """
        transaction commit
        :param t_index: 事务句柄
        :return:
        """
        try:
            trans_conn = self.__transaction.get(t_index)
            if trans_conn is None:
                log.error('t_index : trans fail because is t_index not find')
                return True
            await trans_conn.commit()
        except Exception as error:
            log.error(error)
            await self.rollback(t_index)
            return False

        return True

    async def rollback(self, t_index: str) -> bool:
        """
        transaction rollback
        :param t_index: 事务句柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        await trans_conn.rollback()

    async def release(self, t_index: str = None):
        """
        connect release
        :param t_index: 事务句柄
        :return:
        """
        # 收回正在使用的链接
        trans_conn = self.__transaction[t_index]
        trans_cur = self.__transaction_cur[t_index]
        await trans_cur.close()
        self.pool.release(trans_conn)
        self.__transaction.pop(t_index, None)
        self.__transaction_cur.pop(t_index, None)

    async def close(self):
        """
        关闭连接池
        """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


class pyMysqlDb(object):
    # 生成同步的
    def __init__(self, conn_conf, pool_conf=None):
        """
        初始化一个 pool
        :param conn_conf: mysql 链接配置参数
        :param pool_conf: pool 配置参数
        """
        self.host = conn_conf["host"]
        self.port = conn_conf["port"]
        self.pwd = conn_conf["pwd"]
        self.user = conn_conf["user"]
        self.db = conn_conf["db"]
        self.__transaction = {}  # transaction
        self.__transaction_cur = {}
        pool_conf = pool_conf or {}
        self.Pool = PooledDB(creator=pymysql,
                             mincached=pool_conf.get("mincached", 2),
                             maxcached=pool_conf.get("maxcached", 3),
                             maxshared=pool_conf.get("maxshared", 0),
                             maxconnections=pool_conf.get("maxconnections", 3),
                             use_unicode=True,
                             blocking=True,
                             # pool_recycle=3600,
                             host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.db,
                             autocommit=False,
                             cursorclass=pymysql.cursors.DictCursor,
                             connect_timeout=10,
                             charset="utf8")

    def get_connect(self):
        # 获取数据库连接
        self.conn = self.Pool.connection()
        cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        if not cur:
            return None
        else:
            return cur

    def select(self, sql: str, data: Union[dict, list] = None, many: bool = True, t_index: str = None) -> Union[
        Dict, Tuple]:
        log_sql = sql.replace("\n", ' ')
        log.info(f'执行查询sql: {log_sql}; \n 结果: {data}; t_index: {t_index}')
        rows = None

        if t_index:
            cur = self.__transaction_cur[t_index]
            rows = self.__many_or_one_select(cur, sql, data, many)
        else:
            cur = self.get_connect()
            try:
                rows = self.__many_or_one_select(cur, sql, data, many)
            except Exception as e:
                log.error(traceback.format_exc())
            finally:
                cur.close()

        if not rows:
            rows = [] if many else {}
        return rows

    def __many_or_one_select(self, cursor: Union[pymysql.cursors.Cursor, pymysql.cursors.DictCursor],
                             sql: str, data: Union[dict, list] = None, many: bool = True):
        cursor.execute(sql, data)
        if many:
            rows = cursor.fetchall()
            rows = list(rows)
        else:
            rows = cursor.fetchone()
        return rows

    def execute(self, sql, data: dict = None, t_index: str = None) -> bool:
        """
        执行sql
        :param sql:
        :param data: {}
        :param t_index: transaction key (without commit)
        :return:
        """
        relist = True
        log_sql = sql.replace("\n", ' ')
        # log.info(f'执行sql: {log_sql}; \n 结果: {data}; t_index: {t_index}')
        if t_index:
            trans_cur = self.__transaction_cur[t_index]
            trans_cur.execute(sql, data)
        else:
            cur = self.get_connect()
            try:
                relist = cur.execute(sql, data)
                self.conn.commit()
            except BaseException:
                relist = False
                log.error("------------------SQL ERROR: {}".format(traceback.format_exc()))
            finally:
                cur.close()
        return relist

    def executemany(self, sql, data: list = None, t_index=None):
        """
        批量执行
        :param sql: INSERT INTO employees (name, phone) VALUES ('%s','%s')
        :param data: [ (name1, phone1), (name2, phone2) ]
        :param t_index: transaction key (without commit)
        :return:
        """
        log.info("执行SQL: {}, \n 结果: {}".format(sql, data))

        if t_index:
            cur = self.__transaction_cur[t_index]
            cur.executemany(sql, data)
        else:
            cur = self.get_connect()
            try:
                cur.executemany(sql, data)
                self.conn.commit()
            except BaseException:
                log.error("SQL ERROR: {}".format(traceback.format_exc()))
            finally:
                cur.close()
                # self.conn.close()
        return True

    def begin(self, t_index=None, *args, **kwargs):
        """
        transation begin
        :param t_index: 事务句柄
        :param args:
        :param kwargs:
        :return:
        """
        trans_conn = self.Pool.connection()
        if not t_index:
            t_index = str(trans_conn.__hash__())
        self.__transaction[t_index] = trans_conn
        self.__transaction_cur[t_index] = self.__transaction[t_index].cursor(cursor=pymysql.cursors.DictCursor)
        self.__transaction[t_index].begin(*args, **kwargs)
        return t_index

    def commit(self, t_index):
        """
        transaction commit
        :param t_index: 事务句柄
        :return:
        """
        try:
            trans_conn = self.__transaction[t_index]
            trans_conn.commit()
        except Exception as e:
            log.error(traceback.format_exc())

    def rollback(self, t_index):
        """
        transaction rollback
        :param t_index: 事务句柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        trans_conn.rollback()

    def release(self, t_index):
        """
        结束本次事务操作 关闭链接
        :param t_index: 事务句柄
        :return:
        """
        trans_conn = self.__transaction[t_index]
        trans_cur = self.__transaction_cur[t_index]
        trans_cur.close()
        # trans_conn.close()
        self.__transaction.pop(t_index, None)
        self.__transaction_cur.pop(t_index, None)

    def close(self, t_index: str = None):
        """
        connect release
        :param t_index: 事务句柄
        :return:
        """
        self.Pool.close()


def get_database_pool():
    """获取数据库pool"""
    db_pool = {}
    for key, item in environment.BusinessConfig.items():
        dp = AioMysqlDb(**item)
        db_pool.setdefault(key, dp)
    return db_pool


def get_async_database_pool():
    """异步获取数据库pool"""
    db_pool = {}
    for key, item in environment.BusinessConfig.items():
        dp = pyMysqlDb(item)
        db_pool.setdefault(key, dp)
    return db_pool
