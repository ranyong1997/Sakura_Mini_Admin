#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 16:03
# @Author  : 冉勇
# @Site    : 
# @File    : casbinaction_services.py
# @Software: PyCharm
# @desc    : Casbin Action 服务
from sqlalchemy.orm import Session
from back.crud.casbinrule_services import get_casbin_rules_by_act_key
from back.models.db_casbinaction_models import CasbinAction


def create_casbin_action(db: Session, casbinaction: CasbinAction):
    """
    创建casbin行为
    :param db:
    :param casbinaction:
    :return:
    """
    try:
        db.add(casbinaction)
        db.commit()
        return True
    except:
        return False


def add_casbin_action(db: Session, casbinactions):
    """
    添加casbin行为
    :param db:
    :param casbinactions:
    :return:
    """
    for c in casbinactions:
        db.add(c)
    db.commit()


def get_casbin_actions(db: Session):
    """
    获取casbin行为
    :param db:
    :return:
    """
    return db.query(CasbinAction).all()


def get_casbin_action_by_id(db: Session, id: int):
    """
    根据id获取casbin行为
    :param db:
    :param id:
    :return:
    """
    return db.query(CasbinAction).filter_by(id=id).first()


def get_casbin_action_count(db: Session):
    """
    获取casbin行为数量
    :param db:
    :return:
    """
    return db.query(CasbinAction).count()


def update_casbin_action(db: Session, old_id: int, name: str, action_key: str, description: str):
    """
    更新casbin行为
    :param db:
    :param old_id:
    :param name:
    :param action_key:
    :param description:
    :return:
    """
    ca = get_casbin_action_by_id(db, old_id)
    temp_key = ca.action_key
    if ca:
        ca.name = name
        ca.action_key = action_key  # 如果action_key,应当更新CasbinRule里的数据
        ca.description = description
        db.commit()
        if temp_key != action_key:
            crs = get_casbin_rules_by_act_key(db, temp_key)
            for cr in crs:
                cr.v2 = action_key
            db.commit()
        return ca
    else:
        return False


def update_casbin_action_by_id(db: Session, old_id: int, name: str, action_key: str, description: str):
    """
    修改casbin_action
    :param db:
    :param old_id:
    :param name:
    :param action_key:
    :param description:
    :return:
    """
    ca = get_casbin_action_by_id(db, old_id)
    temp_key = ca.action_key
    if ca:
        ca.name = name
        ca.action_key = action_key  # 如果action_key,应当更新CasbinRule里的数据
        ca.description = description
        db.commit()
        if temp_key != action_key:
            crs = get_casbin_rules_by_act_key(db, temp_key)
            for cr in crs:
                cr.v2 = action_key
            db.commit()
        return ca
    else:
        return False


def delete_casbin_action_by_id(db: Session, ac_id: int):
    """
    删除casbin行为，同时删除casbinrule中存在的动作rule
    :param db:
    :param ac_id:
    :return:
    """
    ac = get_casbin_action_by_id(db, ac_id)
    ac_key = ac.action_key
    if ac:
        db.delete(ac)
        crs = get_casbin_rules_by_act_key(db, ac_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        return True
    else:
        return False
