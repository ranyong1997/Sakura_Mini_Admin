#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 16:04
# @Author  : 冉勇
# @Site    : 
# @File    : casbinobject_services.py
# @Software: PyCharm
# @desc    : Casbin Object 服务
from sqlalchemy.orm import Session
from back.crud.casbinrule_services import get_casbin_rules_by_act_key
from back.models.db_casbin_object_models import CasbinObject


def create_casbin_object(db: Session, casbinobject: CasbinObject):
    """
    创建casbin项目
    :param db:
    :param casbinobject:
    :return:
    """
    try:
        db.add(casbinobject)
        db.commit()
        return True
    except:
        return False


def add_casbin_objects(db: Session, casbinobject: CasbinObject):
    """
    添加casbin项目
    :param db:
    :param casbinobject:
    :return:
    """
    for co in casbinobject:
        db.add(co)
    db.commit()


def get_casbin_objects(db: Session):
    """
    获取casbin项目
    :param db:
    :return:
    """
    return db.query(CasbinObject).all()


def get_casbin_object_by_id(db: Session, id: int):
    """
    根据id获取casbin项目
    :param db:
    :param id:
    :return:
    """
    return db.query(CasbinObject).filter_by(id=id).first()


def get_casbin_object_count(db: Session):
    """
    获取casbin_object数量
    :param db:
    :return:
    """
    return db.query(CasbinObject).count()


def update_casbin_object(db: Session, old_id, name, obj_key, description):
    """
    更新casbin项目
    :param db:
    :param old_id:
    :param name:
    :param obj_key:
    :param description:
    :return:
    """
    co = get_casbin_object_by_id(db, old_id)
    if co:
        temp_key = co.object_key
        co.name = name
        co.object_key = obj_key
        co.description = description
        db.commit()
        if temp_key != obj_key:
            cos = get_casbin_rules_by_act_key(db, temp_key)
            for co in cos:
                co.v1 = obj_key
            db.commit()
        return True
    else:
        return False


def delete_casbin_object_by_id(db: Session, ac_id: int):
    """
    根据id删除casbin项目
    :param db:
    :param ac_id:
    :return:
    """
    obj = get_casbin_object_by_id(db, ac_id)
    obj_key = obj.object_key
    if obj:
        db.delete(obj)
        crs = get_casbin_rules_by_act_key(db, obj_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        return True
    else:
        return False
