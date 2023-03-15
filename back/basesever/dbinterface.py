#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:34
# @Author  : 冉勇
# @Site    : 
# @File    : dbinterface.py
# @Software: PyCharm
# @desc    :
from typing import Union, Tuple, Dict
from back.environment.test.db_config import TABLE_DB_MAP
from back.dbdriver import mysql, redis, sync_redis, async_mysql


class DBConnectionFactory(object):

    @classmethod
    def find_dbinterface(cls, db_source=None):
        f_db_source = db_source
        if f_db_source == 'mysql':
            return MySQLDBInterface()
        if f_db_source == 'sync_mysql':
            return SyncMysqlDBInterface()
        elif f_db_source == 'redis':
            return RedisInterface()
        elif f_db_source == 'sync_redis':
            return SyncRedisInterface()
        else:
            raise NotImplementedError


class DBInterface(object):
    """
    数据接口
    """
    DB_SOURCE = None  # mysql

    @property
    def mdb(self):
        return mysql

    @property
    def async_mdb(self):
        return async_mysql

    @property
    def rd(self):
        """异步redis"""
        return redis

    @property
    def sync_rd(self):
        """同步redis"""
        return sync_redis


class MySQLDBInterface(DBInterface):
    # 在这里做跟多简便的操作
    DB_SOURCE = 'mysql'  # mysql
    DE_DB = 'default'
    SELECT_DB = None

    def _get_db(self, table_name: str = None):
        DB = TABLE_DB_MAP.get(table_name, None)
        db = self.SELECT_DB if self.SELECT_DB else DB
        db = db if db else self.DE_DB
        return db

    async def select(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
                     many: bool = True, t_index: str = None) -> Union[Dict, Tuple]:
        """
        :param table_name: 表名, 用于多数据库区分，不传默认就是 使用flowers数据库
        :param sql: 待执行的SQL语句
        :param data: 参数部分
        :param many: 是否返回所有数据，否则只返回第一条
        :param is_need_total: 是否返回查询到数据总条目数
        :param t_index: 事物句柄
        """
        db = self._get_db(table_name)
        return await self.mdb[db].select(sql, data=data, many=many, t_index=t_index)

    async def execute(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
                      t_index: str = None) -> bool:
        """
        :param sql: 待执行的SQL语句
        :param table_name: 表名, 用于多数据库区分，目前不需要传
        :param data: 参数部分
        :param t_index: 事物句柄, 一般用不到
        """
        db = self._get_db(table_name)
        return await self.mdb[db].execute(sql, data=data, t_index=t_index)

    async def executemany(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
                          t_index: str = None) -> bool:
        db = self._get_db(table_name)
        return await self.mdb[db].executemany(sql, data=data, t_index=t_index)

    def get_db_instance(self, db: str = None):
        self.SELECT_DB = db or self.DE_DB
        return self.mdb[self.SELECT_DB]


class SyncMysqlDBInterface(DBInterface):
    # 在这里做跟多简便的操作
    DB_SOURCE = 'sync_mysql'  # mysql
    DE_DB = 'default'
    SELECT_DB = None

    def _get_db(self, table_name: str = None):
        DB = TABLE_DB_MAP.get(table_name, None)
        db = self.SELECT_DB if self.SELECT_DB else DB
        db = db if db else self.DE_DB
        return db

    def select(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
               many: bool = True, t_index: str = None) -> Union[Dict, Tuple]:
        """
        :param table_name: 表名, 用于多数据库区分，不传默认就是 使用flowers数据库
        :param sql: 待执行的SQL语句
        :param data: 参数部分
        :param many: 是否返回所有数据，否则只返回第一条
        :param is_need_total: 是否返回查询到数据总条目数
        :param t_index: 事物句柄
        """
        db = self._get_db(table_name)
        return self.async_mdb[db].select(sql, data=data, many=many, t_index=t_index)

    def execute(self, sql: str, table_name: str = None, data: Union[dict, list] = None, t_index: str = None) -> bool:
        """
        :param sql: 待执行的SQL语句
        :param table_name: 表名, 用于多数据库区分，目前不需要传
        :param data: 参数部分
        :param t_index: 事物句柄, 一般用不到
        """
        db = self._get_db(table_name)
        return self.async_mdb[db].execute(sql, data=data, t_index=t_index)

    def executemany(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
                    t_index: str = None) -> bool:
        db = self._get_db(table_name)
        return self.async_mdb[db].executemany(sql, data=data, t_index=t_index)

    def get_db_instance(self, db: str = None):
        """获取数据库实例"""
        self.SELECT_DB = db or self.DE_DB
        return self.async_mdb[self.SELECT_DB]


class RedisInterface(DBInterface):
    DB_SOURCE = "redis"
    DEFAULT_DB = '11'

    def con(self, db: str = '11'):
        db = db if db is not None else self.DEFAULT_DB
        return self.rd[db].con


class SyncRedisInterface(DBInterface):
    DB_SOURCE = "sync_redis"
    DEFAULT_DB = '11'

    def con(self, db: str = '11'):
        db = db if db is not None else self.DEFAULT_DB
        return self.sync_rd[db].con
