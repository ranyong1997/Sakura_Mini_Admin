#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 11:24
# @Author  : 冉勇
# @Site    : 
# @File    : MysqlJobStore.py
# @Software: PyCharm
# @desc    : mysql连接方式
from __future__ import absolute_import

import traceback

from apscheduler.jobstores.base import BaseJobStore, JobLookupError, ConflictingIdError
from apscheduler.util import datetime_to_utc_timestamp, utc_timestamp_to_datetime
from apscheduler.job import Job
from back.utils.logger import log
try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle
import pymysql
from dbutils.pooled_db import PooledDB


class mysqlManager(object):
    """
    mysql 操作对象
    """

    def __init__(self, conn_conf: dict = None, pool_conf={}, echo=False):
        """
        初始化一个 pool
        :param conn_conf: mysql 链接配置参数
        :param pool_conf: pool 配置参数
        :param echo: 是否输出日志
        """
        self.echo = echo
        self.host = conn_conf["host"]
        self.port = conn_conf["port"]
        self.pwd = conn_conf["pwd"]
        self.user = conn_conf["user"]
        self.db = conn_conf["db"]
        self.__transaction = {}  # transaction
        self.__transaction_cur = {}
        self.pool_conf = pool_conf or {}
        self.Pool = PooledDB(creator=pymysql, mincached=pool_conf.get("mincached", 2),
                             maxcached=pool_conf.get("maxcached", 3),
                             maxshared=pool_conf.get("maxshared", 0),
                             maxconnections=pool_conf.get("maxconnections", 3),
                             blocking=True,
                             host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.db,
                             charset="utf8mb4")

    def _getConnectCur(self):
        self.conn = self.Pool.connection()
        cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        if not cur:
            return None
        else:
            return cur

    def fetchmany(self, sql: str, data: dict = None) -> list:
        """
        fetch all
        :param sql: sql语句
        :param data: sql中需要的参数
        :return:
        """
        if self.echo:
            log.info(f"fetchmany: {sql} ; data: {data}")

        relist = []
        cur = self._getConnectCur()
        try:
            cur.execute(sql, data)
            relist = cur.fetchall()
            relist = list(relist)
        except BaseException:
            pass
        finally:
            cur.close()
        return relist

    def fetchone(self, sql: str, data: dict = None) -> dict:
        """
        查询单条
        :param sql: sql语句
        :param data: sql中需要的参数
        :return:
        """
        if self.echo:
            log.info(f"fetchone: {sql} ; data: {data}")
        relist = {}
        cur = self._getConnectCur()
        try:
            cur.execute(sql, data)
            relist = cur.fetchone()
        except BaseException:
            pass
        finally:
            cur.close()
            # self.conn.close()
        return relist

    def execute(self, sql: str, data: dict = None) -> bool:
        """
        执行sql
        :param sql: sql语句
        :param data: sql参数
        :return:
        """
        relist = 0
        if self.echo:
            log.info(f"execute: {sql} ; data: {data}")

        cur = self._getConnectCur()
        try:
            relist = cur.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            raise e
        finally:
            cur.close()
        return relist

    def close(self):
        """
        关闭
        :return:
        """
        self.Pool.close()


class MysqlJobStore(BaseJobStore):

    def __init__(self, config: dict = None, pool=None, table_name="apscheduler_task", echo=False,
                 pickle_protocol=pickle.HIGHEST_PROTOCOL):
        super(MysqlJobStore, self).__init__()

        if pool:
            self.jobs_t = pool
        else:
            self.jobs_t = mysqlManager(conn_conf=config, echo=echo)
        self.table_name = table_name
        self.pickle_protocol = pickle_protocol

    def start(self, scheduler, alias):
        super(MysqlJobStore, self).start(scheduler, alias)
        self.jobs_t.execute(f"""
                    create table if not exists {self.table_name}(
                      `id` varchar(191) NOT NULL,
                      `next_run_time` double DEFAULT NULL,
                      `job_state` blob NOT NULL,
                      PRIMARY KEY (`id`),
                      KEY `ix_api_job_next_run_time` (`next_run_time`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

    def lookup_job(self, job_id):
        sql = f"select job_state from {self.table_name} where id='{job_id}'"
        job_state = self.jobs_t.fetchone(sql=sql)
        job_state = job_state['job_state'] if job_state else None
        return self._reconstitute_job(job_state) if job_state else None

    def get_due_jobs(self, now):
        timestamp = datetime_to_utc_timestamp(now)
        return self._get_jobs(f"where next_run_time <= {timestamp}")

    def get_next_run_time(self):
        sql = f"select next_run_time from {self.table_name} where next_run_time is not null order by next_run_time limit 1"
        next_run_time = self.jobs_t.fetchone(sql=sql)
        next_run_time = next_run_time['next_run_time'] if next_run_time else None
        return utc_timestamp_to_datetime(next_run_time)

    def get_all_jobs(self):
        jobs = self._get_jobs()
        self._fix_paused_jobs_sorting(jobs)
        return jobs

    def add_job(self, job):
        try:
            sql = f"""insert into {self.table_name}(id, next_run_time, job_state)
             values(%(job_id)s, %(next_run_time)s, %(job_state)s)"""
            data = {
                "job_id": job.id,
                "next_run_time": datetime_to_utc_timestamp(job.next_run_time),
                "job_state": pickle.dumps(job.__getstate__(), self.pickle_protocol)}
            self.jobs_t.execute(sql=sql, data=data)
        except pymysql.err.IntegrityError as e:
            raise ConflictingIdError(job.id)
        except Exception as e:
            log.error(f'add job error : {type(e)}')

    def update_job(self, job):
        try:
            data = {
                'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
                'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol)
            }
            sql = f"update {self.table_name} set next_run_time=%(next_run_time)s, job_state=%(job_state)s where id='{job.id}'"
            self.jobs_t.execute(sql=sql, data=data)
        except Exception as e:
            raise JobLookupError(job.id)

    def remove_job(self, job_id):

        sql = f"delete from {self.table_name} where id='{job_id}'"
        result = self.jobs_t.execute(sql=sql)
        if not result:
            raise JobLookupError(job_id)

    def remove_all_jobs(self):
        self.jobs_t.execute(sql=f'TRUNCATE TABLE {self.table_name}')

    def shutdown(self):
        # self.engine.dispose()
        self.jobs_t.Pool.close()

    def _reconstitute_job(self, job_state):
        job_state = pickle.loads(job_state)
        job_state['jobstore'] = self
        job = Job.__new__(Job)
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job

    def _get_jobs(self, conditions=None):
        jobs = []
        sql = f"""
            select id, job_state from {self.table_name} 
        """
        sql = sql + conditions if conditions else sql

        failed_job_ids = set()
        for row in self.jobs_t.fetchmany(sql):
            try:
                jobs.append(self._reconstitute_job(row['job_state']))
            except BaseException:
                self._logger.exception('Unable to restore job "%s" -- removing it', row['id'])
                failed_job_ids.add(row['id'])

        # Remove all the jobs we failed to restore
        if failed_job_ids:
            sql = f"""
                delete from {self.table_name} where id in %(failed_job_ids)s
            """
            # delete = self.jobs_t.delete().where(self.jobs_t.c.id.in_(failed_job_ids))
            # self.engine.execute(delete)
            self.jobs_t.execute(sql=sql, data={"failed_job_ids": list(failed_job_ids)})
        return jobs

    def __repr__(self):
        return '<%s (url=%s)>' % (self.__class__.__name__, self.jobs_t.host)
