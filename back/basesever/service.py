#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:33
# @Author  : 冉勇
# @Site    : 
# @File    : service.py
# @Software: PyCharm
# @desc    : 封装对mysql增删改查
import uuid
import re
from typing import Union, Tuple, Dict, List, Any
from inspect import isfunction
from back.basesever.dbinterface import DBConnectionFactory
from back.utils.time_handler import time_remaining


class MysqlBaseService(object):
    DB_SOURCE = 'mysql'

    # 这里更多的对sql 数据处理

    def __init__(self):
        self.db_interface = DBConnectionFactory.find_dbinterface(self.DB_SOURCE)
        self.t_index = None
        self.db = None

    async def __aenter__(self):
        """
        开启事务, 如果跨了 实例执行事务， 需要拿这里的 t_index, t_index是整个进程独一份的 事务句柄
        """
        if self.t_index is None:
            self.t_index = await self.db_interface.get_db_instance(db=self.db).begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        事务执行时，无论是否发生错误都会执行 释放链接，是链接返回链接池
        """
        if not exc_type:
            # 如果忘记执行提交了, 且没有异常发生， 这里会自动提交
            await self.db_interface.get_db_instance(db=self.db).commit(self.t_index)
        else:
            # 发生异常直接回滚
            await self.db_interface.get_db_instance(db=self.db).rollback(self.t_index)
        # 提交后或回滚后 自动释放链接
        await self.db_interface.get_db_instance(db=self.db).release(self.t_index)
        self.t_index = None

    def __call__(self, *args, **kwargs):
        """
        指定数据库， 这里有默认的， 当多数据库的时候 需要用这个
        """
        self.db = kwargs.get('db', None)
        return self

    async def select(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
                     t_index: str = None) -> dict:
        t_index = t_index if t_index else self.t_index
        return await self.db_interface.select(sql, table_name=table_name, data=data, many=False, t_index=t_index)

    async def fetchmany(self, sql: str = None, table_name: str = None, data: Union[dict, list] = None,
                        t_index: str = None) -> list:
        t_index = t_index if t_index else self.t_index
        return await self.db_interface.select(sql, table_name=table_name, data=data, many=True, t_index=t_index)

    async def fetchmany_with_total(self, sql: str = None, table_name: str = None,
                                   data: Union[dict, list] = None, t_index: str = None) -> tuple:
        """
        传入正常的查询语句， 内部自动替换 select * from table_name ... limit 2,20 为 select count(1) as total from table_name ...
        limit 0,10 只会替换最后一个
        """
        sql = sql.strip()
        # 匹配替换, 去掉结尾的limit , 替换第一个select 到from的字符为 count(1) as total
        total_sql = re.sub(r"(^select.*?from |limit \d+\s*,\s*\d+$|limit \S+\s*,\s*\S+$)",
                           lambda m: 'select count(1) as total from ' if "select" in m.group(0) else "",
                           sql, flags=re.S)
        # 接着上面 去掉 语句结尾的 order 语句
        total_sql = re.sub(r'order\s*by\s*\S+\s*desc$|order\s*by\s*\S+\s*asc$|', '', total_sql.strip(), flags=re.S)

        t_index = t_index if t_index else self.t_index
        total = await self.db_interface.select(total_sql, table_name=table_name, data=data, many=False, t_index=t_index)
        rows = await self.db_interface.select(sql, table_name=table_name, data=data, many=True, t_index=t_index)
        return rows, total['total'] if total else 0

    async def execute(self, sql: str = None, data: Union[dict, list] = None, table_name: str = None,
                      t_index: str = None):
        t_index = t_index if t_index else self.t_index
        return await self.db_interface.execute(sql, table_name=table_name, data=data, t_index=t_index)

    async def executemany(self, sql: str = None, table_name: str = None, data: Union[list] = None, t_index: str = None):
        return await self.db_interface.executemany(sql=sql, data=data, table_name=table_name, t_index=t_index)

    async def insert_or_update(self, table_name: str = None, values: Union[List[Dict], Dict] = None,
                               update_name: List = [], t_index: str = None):
        """
        插入或更新数据库
        :param table_name: 数据表名
        :param values: 插入的数据, key 要与数据库的属性一致
        :param update_name: 当主键存在时， 更新那些数据， 数组中是字符串则必须出现在values中 ["name", "ki"]| [{"key": "age", "value": "age * 2"}]
        :param t_index: 事物句柄
        :return:
        """
        sql = """ insert into {table_name}{keys} values{values}  """

        if not values:
            return

        temp_data = values[0] if isinstance(values, list) else values

        key_str = list()
        value_name = list()
        for key in temp_data.keys():
            value_name.append(f"%({key})s")
            key_str.append(f"`{key}`")

        key_str = "( " + ", ".join(key_str) + " )"
        value_name = "( " + ", ".join(value_name) + " )"

        sql = sql.format(table_name=table_name, keys=key_str, values=value_name)

        if update_name:
            update_ = []
            for up_d in update_name:
                if isinstance(up_d, str):
                    update_.append(f" `{up_d}` = values({up_d})  ")
                elif isinstance(up_d, dict):
                    """
                    {
                        "key": "yu",
                        "value": "%(yu)s"
                    }
                    """
                    update_.append(f"`{up_d['key']}` = {up_d['value']} ")
            update_str = ", ".join(update_)

            sql = " ON DUPLICATE KEY UPDATE ".join([sql, update_str])

        t_index = t_index if t_index else self.t_index
        if isinstance(values, list):
            return await self.db_interface.executemany(sql, table_name=table_name, data=values, t_index=t_index)
        else:
            return await self.db_interface.execute(sql, table_name=table_name, data=values, t_index=t_index)

    async def update(self, table_name: str = None, values: Dict = None, where: Dict = None, t_index: str = None):
        """
        更新数据库
        :param table_name: 表名
        :param values: 要更新的数据 key 属性名， value 要更新的值
        :param where: 条件 key 属性名， value用于判断的 值
        :param t_index: 事务句柄
        """
        if not where or not table_name or not values:
            raise

        value_name = list()
        set_copy = {}
        for key, value in values.items():
            if isinstance(value, dict):
                # "{"value": `key` + 1}"
                value_name.append(f"`{key}` = {value['value']}")
            else:
                set_copy[f"va_{key}"] = value
                value_name.append(f"`{key}` = %(va_{key})s ")

        eql_value = ", ".join(value_name)

        where_v = list()
        for wh, value in where.items():
            set_copy[f"wh_{wh}"] = value
            if isinstance(value, list):
                where_v.append(f"`{wh}` in %(wh_{wh})s")
            else:
                where_v.append(f"`{wh}` = %(wh_{wh})s")

        where_str = " and ".join(where_v)

        sql = f"""  update {table_name} set {eql_value} where {where_str} """

        t_index = t_index if t_index else self.t_index
        return await self.db_interface.execute(sql=sql, table_name=table_name, data=set_copy, t_index=t_index)


class SyncMysqlBaseService(object):
    DB_SOURCE = 'sync_mysql'

    # 这里更多的对sql 数据处理

    def __init__(self):
        self.db_interface = DBConnectionFactory.find_dbinterface(self.DB_SOURCE)
        self.t_index = None
        self.db = None

    def __enter__(self):
        """
        开启事务, 如果跨了 实例执行事务， 需要拿这里的 t_index, t_index是整个进程独一份的 事务句柄
        """
        if self.t_index is None:
            self.t_index = self.db_interface.get_db_instance(db=self.db).begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        事务执行时，无论是否发生错误都会执行 释放链接，是链接返回链接池
        """
        if not exc_type:
            # 如果忘记执行提交了, 且没有异常发生， 这里会自动提交
            self.db_interface.get_db_instance(db=self.db).commit(self.t_index)
        else:
            # 发生异常直接回滚
            self.db_interface.get_db_instance(db=self.db).rollback(self.t_index)
        # 提交后或回滚后 自动释放链接
        self.db_interface.get_db_instance(db=self.db).release(self.t_index)
        self.t_index = None

    def __call__(self, *args, **kwargs):
        """
        指定数据库， 这里有默认的， 当多数据库的时候 需要用这个
        """
        self.db = kwargs.get('db', None)
        return self

    def select(self, sql: str, table_name: str = None, data: Union[dict, list] = None,
               t_index: str = None) -> dict:
        t_index = t_index if t_index else self.t_index
        return self.db_interface.select(sql, table_name=table_name, data=data, many=False, t_index=t_index)

    def fetchmany(self, sql: str = None, table_name: str = None, data: Union[dict, list] = None,
                  t_index: str = None) -> list:
        t_index = t_index if t_index else self.t_index
        return self.db_interface.select(sql, table_name=table_name, data=data, many=True, t_index=t_index)

    def fetchmany_with_total(self, sql: str = None, table_name: str = None,
                             data: Union[dict, list] = None, t_index: str = None) -> tuple:
        """
        传入正常的查询语句， 内部自动替换 select * from table_name ... limit 2,20 为 select count(1) as total from table_name ...
        limit 0,10 只会替换最后一个
        """
        sql = sql.strip()
        # 匹配替换, 去掉结尾的limit , 替换第一个select 到from的字符为 count(1) as total
        total_sql = re.sub(r"(^select.*?from |limit \d+\s*,\s*\d+$|limit \S+\s*,\s*\S+$)",
                           lambda m: 'select count(1) as total from ' if "select" in m.group(0) else "",
                           sql, flags=re.S)
        # 接着上面 去掉 语句结尾的 order 语句
        total_sql = re.sub(r'order\s*by\s*\S+\s*desc$|order\s*by\s*\S+\s*asc$|', '', total_sql.strip(), flags=re.S)

        t_index = t_index if t_index else self.t_index
        total = self.db_interface.select(total_sql, table_name=table_name, data=data, many=False, t_index=t_index)
        rows = self.db_interface.select(sql, table_name=table_name, data=data, many=True, t_index=t_index)
        return rows, total['total'] if total else 0

    def execute(self, sql: str = None, data: Union[dict, list] = None, table_name: str = None, t_index: str = None):
        t_index = t_index if t_index else self.t_index
        if isinstance(data, list):
            return self.db_interface.executemany(sql, table_name=table_name, data=data, t_index=t_index)
        else:
            return self.db_interface.execute(sql, table_name=table_name, data=data, t_index=t_index)

    def insert_or_update(self, table_name: str = None, values: Union[List[Dict], Dict] = None,
                         update_name: List = [], t_index: str = None):
        """
        插入或更新数据库
        :param table_name: 数据表名
        :param values: 插入的数据, key 要与数据库的属性一致
        :param update_name: 当主键存在时， 更新那些数据， 数组中是字符串则必须出现在values中 ["name", "ki"]| [{"key": "age", "value": "age * 2"}]
        :param t_index: 事物句柄
        :return:
        """
        sql = """ insert into {table_name}{keys} values{values}  """

        if not values:
            return

        temp_data = values[0] if isinstance(values, list) else values

        key_str = list()
        value_name = list()
        for key in temp_data.keys():
            value_name.append(f"%({key})s")
            key_str.append(f"`{key}`")

        key_str = "( " + ", ".join(key_str) + " )"
        value_name = "( " + ", ".join(value_name) + " )"

        sql = sql.format(table_name=table_name, keys=key_str, values=value_name)

        if update_name:
            update_ = []
            for up_d in update_name:
                if isinstance(up_d, str):
                    update_.append(f" `{up_d}` = values({up_d}) ")
                elif isinstance(up_d, dict):
                    """
                    {
                        "key": "yu",
                        "value": "%(yu)s"
                    }
                    """
                    update_.append(f"`{up_d['key']}` = {up_d['value']} ")
            update_str = ", ".join(update_)

            sql = " ON DUPLICATE KEY UPDATE ".join([sql, update_str])

        t_index = t_index if t_index else self.t_index
        if isinstance(values, list):
            return self.db_interface.executemany(sql, table_name=table_name, data=values, t_index=t_index)
        else:
            return self.db_interface.execute(sql, table_name=table_name, data=values, t_index=t_index)

    def update(self, table_name: str = None, values: Dict = None, where: Dict = None, t_index: str = None):
        """
        更新数据库
        :param table_name: 表名
        :param values: 要更新的数据 key 属性名， value 要更新的值
        :param where: 条件 key 属性名， value用于判断的 值
        :param t_index: 事务句柄
        """
        if not where or not table_name or not values:
            raise

        value_name = list()
        set_copy = {}
        for key, value in values.items():
            if isinstance(value, dict):
                # "{"value": `key` + 1}"
                value_name.append(f"`{key}` = {value['value']}")
            else:
                set_copy[f"va_{key}"] = value
                value_name.append(f"`{key}` = %(va_{key})s ")

        eql_value = ", ".join(value_name)

        where_v = list()
        for wh, value in where.items():
            set_copy[f"wh_{wh}"] = value
            if isinstance(value, list):
                where_v.append(f"`{wh}` in %(wh_{wh})s")
            else:
                where_v.append(f"`{wh}` = %(wh_{wh})s")

        where_str = " and ".join(where_v)

        sql = f"""  update {table_name} set {eql_value} where {where_str} """

        t_index = t_index if t_index else self.t_index
        return self.db_interface.execute(sql=sql, table_name=table_name, data=set_copy, t_index=t_index)

    def update_many(self, table_name: str = None, values: Union[List[Dict], Dict] = None,
                    set_name: List = None, where: list = None, t_index: str = None):
        """
        更新数据库
        :param table_name: 表名
        :param values: 要更新的数据 key 属性名， value 要更新的值
        :set_name: 需要更新的属性名
        :param where: 条件 key 属性名， value用于判断的 值
        :param t_index: 事务句柄
        """
        if not where or not table_name or not values:
            raise

        value_list = list()
        for set_item in set_name:
            value_list.append(f"`{set_item}` = %({set_item})s ")
        eql_value = ", ".join(value_list)

        where_list = list()
        for where_item in where:
            where_list.append(f"`{where_item}`=%({where_item})s")

        where_str = " and ".join(where_list)

        sql = f"""  update {table_name} set {eql_value} where {where_str} """

        t_index = t_index if t_index else self.t_index

        return self.db_interface.executemany(sql, table_name=table_name, data=values, t_index=t_index)


class RedisBaseService(object):
    DB_SOURCE = 'redis'

    # 这里更多的是对数据处理

    def __init__(self):
        self.db_interface = DBConnectionFactory.find_dbinterface(db_source=self.DB_SOURCE)

    def con(self, db: str = '11'):
        return self.db_interface.con(db=db)

    def cook_redis_key(self, redis_key: Union[dict, str], **kwargs) -> Tuple:
        """
        处理redis_keys中定义的键值
            :param redis_key: redis_keys
            :param kwargs: redis_keys中键的替换参数
        """
        ex = kwargs.get("ex") or 0
        if isinstance(redis_key, str):
            return redis_key, ex, None
        elif isinstance(redis_key, dict):
            key = redis_key['key'].format(**kwargs)
            ex_ = redis_key.get('exp', 0)
            if not ex and isfunction(ex_):
                ex = ex_()
            elif not ex and isinstance(ex_, str) and ex_ in ["day", "week", "month", "year"]:
                ex = time_remaining(type_=ex_)
            elif not ex and isinstance(ex_, int):
                ex = ex_
            else:
                ex = 0
            return key, ex, redis_key.get('db', '13')

    async def get(self, key: Union[Dict, str], db: str = None, **kwargs):
        """
        从Redis中获取值
            :param key: Redis的键
            :param db: 使用的redis的库
            :param kwargs: 键的参数部分
        """
        key, _, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db

        return await self.db_interface.con(db=db).get(key)

    async def set(self, key: Union[Dict, str], value: Any, db=None, **kwargs):
        """
        向Redis中设置单个键的值
            :param key: Redis的键
            :param value: Redis的值
            :param db: 使用的redis库
            :param kwargs: 键的参数部分
        """
        key, ex, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db

        if ex > 0:
            return await self.db_interface.con(db=db).set(key, value=value, ex=ex)
        else:
            return await self.db_interface.con(db=db).set(key, value=value)

    async def sadd(self, key: Union[Dict, str], values: list, db=None, **kwargs):
        key, ex, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db

        if ex > 0:
            res = await self.db_interface.con(db=db).sadd(key, *values)
            await self.db_interface.con(db=db).expire(key, ex)
        else:
            return await self.db_interface.con(db=db).set(key, *values)

    async def sdiff(self, key1: Union[Dict, str], key2: Union[Dict, str], db=None, **kwargs):
        key1, _, r_db = self.cook_redis_key(key1, **kwargs)
        key2, _, _ = self.cook_redis_key(key2, **kwargs)
        await self.db_interface.con(db=db).sdiff(key1, key2)

    async def delete(self, key: Union[Dict, str], db=None, **kwargs):
        """
        Redis中某个键的值自减指定值
            :param key: Redis的键
            :param db: 选择的redis库
            :param kwargs: 键的参数部分
        """
        key, ex, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db
        return await self.db_interface.con(db=db).delete(key)

    async def pipeline(self, data: Union[list], db=None):
        """
        :param data: [{"key": [key, expire], "values": "", "op": "get|set", "kwargs": {}}]
        :param pipe: pipe: Pipeline,
        :param db:
        :return:
        """
        if not db:
            # pipeline中的 db必须都要一样
            db = data[0]['key']['db']

        connect = self.con(db=db)
        pipe = connect.pipeline()
        keys = []
        for ve in data:
            if (kwargs := ve.get('kwargs', None)) is None:
                kwargs = {}
            key, expire = self.cook_redis_key(ve['key'], **kwargs)
            keys.append(f"{ve['op'] if ve.get('op') else 'get'}@{key}")
            if not ve.get('op') or ve['op'] == 'get':
                await pipe.get(key)
            elif ve['op'] == 'set':
                if expire > 0:
                    await pipe.set(key, ve['value'], ex=expire)
                else:
                    await pipe.set(key, ve['value'])

        res = await pipe.execute()
        return dict(zip(keys, res))

    async def aps_lock(self, lock_name: dict, time_out: int = 60, db: str = None) -> bool:
        identifier = str(uuid.uuid4())
        rdb = db if db is not None else lock_name['db']

        connect = self.con(db=rdb)
        # 1 不存在,key被设置
        # 0  已存在,key没有被改变,
        aps = await connect.setnx(lock_name['key'], identifier)
        await connect.expire(lock_name['key'], time_out)
        if aps:
            return True
        return False


class SyncRedisBaseService(object):
    """同步redis"""
    DB_SOURCE = 'sync_redis'

    # 这里更多的是对数据处理
    def __init__(self):
        self.db_interface = DBConnectionFactory.find_dbinterface(db_source=self.DB_SOURCE)

    def con(self, db: str = '11'):
        return self.db_interface.con(db=db)

    def cook_redis_key(self, redis_key: Union[dict, str], **kwargs) -> Tuple:
        """
        处理redis_keys中定义的键值
            :param redis_key: redis_keys
            :param kwargs: redis_keys中键的替换参数
        """
        ex = kwargs.get("ex") or 0
        if isinstance(redis_key, str):
            return redis_key, ex, None
        elif isinstance(redis_key, dict):
            key = redis_key['key'].format(**kwargs)
            ex_ = redis_key['exp']
            if not ex and isfunction(ex_):
                ex = ex_()
            elif not ex and isinstance(ex_, str) and ex_ in ["day", "week", "month", "year"]:
                ex = time_remaining(type_=ex_)
            elif not ex and isinstance(ex_, int):
                ex = ex_
            else:
                ex = 0
            return key, ex, redis_key.get('db', '13')

    def get(self, key: Union[dict, str], db: str = None, **kwargs):
        """
        从Redis中获取值
            :param key: Redis的键
            :param db: 使用的redis的库
            :param kwargs: 键的参数部分
        """
        key, _, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db
        return self.db_interface.con(db=db).get(key)

    def set(self, key: Union[dict, str], value: Any, db=None, **kwargs):
        """
        向Redis中设置单个键的值
            :param key: Redis的键
            :param value: Redis的值
            :param db: 使用的redis库
            :param kwargs: 键的参数部分
        """
        key, ex, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db

        if ex > 0:
            return self.db_interface.con(db=db).set(key, value=value, ex=ex)
        else:
            return self.db_interface.con(db=db).set(key, value=value)

    def delete(self, key: Union[dict, str], db=None, **kwargs):
        """
        Redis中某个键的值自减指定值
            :param key: Redis的键
            :param db: 选择的redis库
            :param kwargs: 键的参数部分
        """
        key, _, r_db = self.cook_redis_key(key, **kwargs)
        if not db:
            db = r_db
        return self.db_interface.con(db=db).delete(key)

    def pipeline(self, data: Union[list], db=None):
        """
        :param data: [{"key": [key, expire], "values": "", "op": "get|set", "kwargs": {}}]
        :param pipe: pipe: Pipeline,
        :param db:
        :return:
        """
        if not db:
            # pipeline中的 db必须都要一样
            db = data[0]['key']['db']

        connect = self.con(db=db)
        pipe = connect.pipeline()
        keys = []
        for ve in data:
            if (kwargs := ve.get('kwargs', None)) is None:
                kwargs = {}
            key, expire, _ = self.cook_redis_key(ve['key'], **kwargs)
            keys.append(f"{ve['op'] if ve.get('op') else 'get'}@{key}")
            if not ve.get('op') or ve['op'] == 'get':
                pipe.get(key)
            elif ve['op'] == 'set':
                if expire > 0:
                    pipe.set(key, ve['value'], ex=expire)
                else:
                    pipe.set(key, ve['value'])
            elif ve['op'] == 'sadd':
                pipe.sadd(key, ve['value'])
                if expire > 0:
                    pipe.expire(key, expire)
            elif ve['op'] == 'smembers':
                pipe.smembers(key)
            elif ve['op'] == 'del':
                pipe.delete(key)

        res = pipe.execute()
        return dict(zip(keys, res))

    def aps_lock(self, lock_name: dict, time_out: int = 60, db: str = None) -> bool:
        identifier = str(uuid.uuid4())
        db = lock_name['db']
        connect = self.con(db=db)
        # 1 不存在,key被设置
        # 0  已存在,key没有被改变,
        aps = connect.setnx(lock_name['key'], identifier)
        connect.expire(lock_name['key'], time_out)
        if aps:
            return True
        return False

    def break_aps_lock(self, lock_name: dict, db: str = None):
        db = lock_name['db']
        self.con(db=db).delete(lock_name['key'])
