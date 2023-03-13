#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 14:07
# @Author  : 冉勇
# @Site    : 
# @File    : tasks_router.py
# @Software: PyCharm
# @desc    :
import traceback
import uuid
from typing import Union
from apscheduler.jobstores.base import JobLookupError
from fastapi import APIRouter, HTTPException
from back.schemas import tasks_schemas
from back.utils.core.init_scheduler import scheduler
from back.utils.logger import log

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)


@router.get("/jobs", response_model=tasks_schemas.QueryResponse)
async def get_jobs(verbose: bool = False):
    """
     查询所有任务


    ### Response
    ---
        成功：
           {
              "message": "Successfully query",
              "status_code": 1,
              "jobs": [
                {
                  "id": "new_book",
                  "name": "start_book",
                  "func": "back.tasks.sources.new_book:start_book",
                  "args": [],
                  "kwargs": {},
                  "executor": "default",
                  "jobstore": "default",
                  "misfire_grace_time": 1800,
                  "coalesce": false,
                  "max_instances": 1,
                  "next_run_time": "2022-10-06T13:33:22.117516+08:00"
                },
               ...
              ]
            }
    """

    jobs = []
    try:
        job_list = scheduler.get_jobs()
        if job_list:
            jobs = [tasks_schemas.Job(**task.__getstate__()) for task in job_list]

        if verbose:
            log.info(jobs)
    except Exception as e:
        log.error(e.args)
        return tasks_schemas.QueryResponse(
            message=f"Failed query {e.args}",
            status_code=0,
            jobs=jobs,
        )

    return tasks_schemas.QueryResponse(
        message="Successfully query",
        status_code=1,
        jobs=jobs,
    )


@router.get("/job/{id}", response_model=tasks_schemas.QueryResponse)
async def get_job_by_id(id: Union[str, int, uuid.UUID],
                        verbose: bool = False):
    """
    根据任务id, 获取任务

    ### Request Path
    ---
        id: str| int 要查询的任务id

    ### Response
    ---
        成功：
        {
          "message": "Successfully query",
          "status_code": 1,
          "jobs": [
            {
              "id": "new_movie",
              "name": "start_movie",
              "func": "back.tasks.sources.new_movie:start_movie",
              "args": [],
              "kwargs": {},
              "executor": "default",
              "jobstore": "default",
              "misfire_grace_time": 1800,
              "coalesce": false,
              "max_instances": 1,
              "next_run_time": "2022-10-06T14:13:22.117518+08:00"
            }
          ]
        }

    """

    jobs = []
    try:
        job = scheduler.get_job(job_id=id)
        if job:
            data_info = job.__getstate__()
            jobs = [tasks_schemas.Job(**data_info)]

        if verbose:
            log.info(job)
    except Exception as e:
        log.error(e.args)
        return tasks_schemas.QueryResponse(
            message=f"Failed query {e.args}",
            status_code=0,
            jobs=jobs,
        )

    return tasks_schemas.QueryResponse(
        message="Successfully query",
        status_code=1,
        jobs=jobs,
    )


@router.post("/add", response_model=tasks_schemas.OperateResponse)
async def add_job(
        job: tasks_schemas.RequestJob
):
    """
    添加新的任务

    ### Request Body
    ---
        id: str|int  # 任务id, 必须唯一
        name: str # 任务的名字 默认None
        func: str, 任务方法的映射； 模块之间使用 . 链接， 模块与方法之间使用 : 链接
            如： back.tasks.sources.hot_top_music:start_music
        args: Sequence[Optional[str]]  # 任务的 args参数 默认： None
        kwargs: Dict[str, Any]   # 任务的kwargs 参数表  默认：None
        executor: str    # 执行期  默认： default
        jobstore: str     # 存储器 默认： default
        misfire_grace_time:int # 任务执行的抖动时间  默认：30
        coalesce: bool  # 任务是否合并执行 默认： False
        max_instances: int  # 每个任务的最大实例 默认： 1
        next_run_time: str # 任务的下次执行时间 默认: None
        replace_existing: bool  # 存在时是否替换， 默认: False
        trigger: str  # 任务的触发器 date|interval|cron
        trigger_args: Dict # 出发器的参数

    ### Response
    ---
        成功：
            {
                "message": "Successfully add",
                "status_code": 1,
                "type": "add"
            }

        失败:
            {
                "message": "Some internal error happened: {err}",
                "status_code": 500,
                "type": "add"
            }

    ### Example:
        {
          "id": "new_music",
          "name": "start_music",
          "func": "back.tasks.sources.hot_top_music:start_music",
          "args": [],
          "kwargs": {},
          "executor": "default",
          "jobstore": "default",
          "misfire_grace_time": 86400,
          "coalesce": false,
          "max_instances": 1,
          "next_run_time": null,
          "replace_existing": true,
          "trigger": "date",
          "trigger_args": {
            "run_date": "2022-10-06 13:45:56"
          }
        }

    """

    try:
        data = job.dict()
        log.info(f'add job {data}')
        trigger_args = {}
        if 'trigger_args' in data:
            trigger_args = data.pop('trigger_args')
        if not data['next_run_time']:
            # 当这个参数为空的时候， 就不要在出现在add_job的参数里， 否则这个任务永远不会执行
            # 因为源码里   有这个判断  if not hasattr(job, 'next_run_time')
            data.pop('next_run_time')
        log.info(f'add job data: {data}; trigger_args: {trigger_args}')

        job = scheduler.add_job(
            **data,
            **trigger_args
        )
    except Exception as e:
        log.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Some internal error happened: {e.args}",
        )
    return tasks_schemas.OperateResponse(
        message="Successfully add",
        status_code=1,
        type="add",
    )


@router.put("/reschedule")
async def reschedule_job(res: tasks_schemas.Rescheduler):
    """
    根据任务id, 修改任务信息

    对于 interval : 不传start_time 默认就是 now() + interval

    ### Request Body
    ---
        id: str|int 要暂停的任务的id
        trigger： str 触发器  date｜interval｜cron
        trigger_args：dict 触发器参数

    ### Response
    ---
        成功：
            {
                "message": "Successfully reschedule",
                "status_code": 1,
                "type": "reschedule"
            }

        失败:
            {
                "message": "Failed reschedule: {err}",
                "status_code": 0,
                "type": "reschedule"
            }
    """
    try:
        scheduler.reschedule_job(
            job_id=res.id, trigger=res.trigger.value, **res.trigger_args
        )
    except JobLookupError as e:
        log.error(e.args)
        return tasks_schemas.OperateResponse(
            message=f"not find job by id",
            status_code=2,
            type="reschedule",
        )

    except Exception as e:
        log.error(e.args)
        return tasks_schemas.OperateResponse(
            message=f"Failed reschedule: {e.args}",
            status_code=0,
            type="reschedule",
        )
    return tasks_schemas.OperateResponse(
        message="Successfully reschedule",
        status_code=1,
        type="reschedule",
    )


@router.put("/pause/{id}")
async def pause_job(id: Union[str, int, uuid.UUID]):
    """
    根据任务id, 暂停任务

    ### Request Path
    ---
        id: str|int 要暂停的任务的id

    ### Response
    ---
        成功：
            {
                "message": "Successfully resume <id:{id}> job",
                "status_code": 1,
                "type": "pause"
            }

        失败:
            {
                "message": "Can't find <id:{id}> job",
                "status_code": 0,
                "type": "pause"
            }
    """
    try:
        scheduler.pause_job(job_id=id)
    except Exception as e:
        log.error(e.args)
        return tasks_schemas.OperateResponse(
            message=f"Can't find <id:{id}> job",
            status_code=0,
            type="pause",
        )

    return tasks_schemas.OperateResponse(
        message=f"Successfully pause <id:{id}> job",
        status_code=1,
        type="pause",
    )


@router.put("/resume/{id}")
async def resume_job(id: Union[str, int]):
    """
    根据任务id, 恢复暂停的任务

    ### Request Path
    ---
        id: str|int 要恢复的任务的id

    ### Response
    ---
        成功：
            {
                "message": "Successfully resume <id:{id}> job",
                "status_code": 1,
                "type": "resume"
            }

        失败:
            {
                "message": "Can't find <id:{id}> job",
                "status_code": 0,
                "type": "resume"
            }
    """
    try:
        scheduler.resume_job(job_id=id)
    except Exception as e:
        log.exception(e.args)
        return tasks_schemas.OperateResponse(
            message=f"Can't find <id:{id}> job",
            status_code=0,
            type="resume",
        )
    return tasks_schemas.OperateResponse(
        message=f"Successfully resume <id:{id}> job",
        status_code=1,
        type="resume",
    )


@router.delete("/delete/all")
async def delete_all_jobs():
    """
    删除所有任务

    ### Response
    ---
        成功：
            {
                "message": "Successfully delete all jobs",
                "status_code": 1,
                "type": "delete_all"
            }

        失败:
            {
                "message": "there isn't any scheduled job",
                "status_code": 0,
                "type": "delete"
            }
    """

    try:
        scheduler.remove_all_jobs()
    except Exception:
        return tasks_schemas.OperateResponse(
            message="there isn't any scheduled job",
            status_code=0,
            type="delete",
        )
    return tasks_schemas.OperateResponse(
        message="Successfully delete all jobs",
        status_code=1,
        type="delete_all",
    )


@router.delete("/delete/{id}")
async def delete_job(id: Union[str, int]):
    """
    根据任务id 删除任务
    ### Request Headers
    ---
        无

    ### Request Path
    ---
        id: str|int 要删除的任务的id

    ### Response
    ---
        成功：
            {
                "message": "Successfully delete",
                "status_code": 1,
                "type": "delete"
            }

        失败:
            {
                "message": "failed delete",
                "status_code": 0,
                "type": "delete"
            }
    """
    try:
        scheduler.remove_job(job_id=id)
    except JobLookupError:
        return tasks_schemas.OperateResponse(
            message="failed delete",
            status_code=0,
            type="delete",
        )
    return tasks_schemas.OperateResponse(
        message="Successfully delete",
        status_code=1,
        type="delete",
    )
