#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 16:03
# @Author  : 冉勇
# @Site    : 
# @File    : role_services.py
# @Software: PyCharm
# @desc    : 角色服务
from sqlalchemy.orm import Session
from back.crud.casbinrule_services import delete_p_casbin_rules, create_casbin_rules, get_casbin_rules_by_ptype_g_v1, \
    get_casbin_rules_by_ptype_p_v0
from back.models.db_role_models import Role
from back.models.db_user_models import User


def create_role(db: Session, role: Role):
    """
    创建角色
    :param db:
    :param role:
    :return:
    """
    db.add(role)
    try:
        db.commit()
        return role
    except Exception:
        return False


def add_user(db: Session, user: User):
    """
    添加用户提交数据库方法
    :param db:
    :param user:
    :return: user
    """
    db.add(user)  # 添加用户
    db.commit()  # 提交数据库
    db.refresh(user)  # 刷新数据库
    return user


def get_roles(db: Session):
    """
    获取所有角色
    :param db:
    :return:
    """
    return db.query(Role).all()


def get_role_by_id(db: Session, role_id: int):
    """
    根据role_id查询角色
    :param db:
    :param role_id:
    :return: role
    """
    return db.query(Role).filter_by(id=role_id).first()


def get_users_count(db: Session):
    """
    查询用户数量
    :param db:
    :return: int
    """
    return db.query(User).count()


def get_role_count(db: Session):
    """
    获取角色数量
    :param db:
    :return:
    """
    return db.query(Role).count()


def get_role_by_name(db: Session, name: str):
    """
    根据姓名获取角色
    :param db:
    :param name:
    :return:
    """
    return db.query(Role).filter_by(name=name).first()


def get_role_by_role_key(db: Session, role_key: str):
    """
    根据关键词获取角色
    :param db:
    :param role_key:
    :return:
    """
    return db.query(Role).filter_by(role_key=role_key).first()


def change_role_casbinrules(db: Session, role_key: str, crs: list):
    """
    修改角色所拥有的权限，先删除role在casbinrule里原有的所有数据，然后添加前端发来的所有新数据
    :param db:
    :param role_key:
    :param crs:
    :return:
    """
    try:
        delete_p_casbin_rules(db, role_key)
        create_casbin_rules(db, crs)
        return True
    except Exception:
        return False


def update_role_by_id(db: Session, old_role_id, new_role):
    """
    根据id更新角色
    :param db:
    :param old_role_id:
    :param new_role:
    :return:
    """
    role = get_role_by_id(db, old_role_id)
    old_role_key = role.role_key
    if role:
        role.name = new_role.name
        role.role_key = new_role.role_key
        role.description = new_role.description
        db.commit()
        # 更新相关的casbin_rule关联用户组的role_key
        crs = get_casbin_rules_by_ptype_g_v1(db, old_role_key)
        for cr in crs:
            cr.v1 = new_role.role_key
        db.commit()
        # 更新相关的casbin_rule关联资源动作的role_key
        crs = get_casbin_rules_by_ptype_p_v0(db, old_role_key)
        for cr in crs:
            cr.v0 = new_role.role_key
        db.commit()
        return True
    else:
        return False


def delete_role_by_id(db: Session, role_id):
    """
    根据id删除角色，以及相关的casbin_rule
    :param db:
    :param role_id:
    :return:
    """
    role = get_role_by_id(db, role_id)
    if role:
        # 删除casbin_rule里的用户组
        crs = get_casbin_rules_by_ptype_g_v1(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        # 删除casbin_rule里的相关rule
        crs = get_casbin_rules_by_ptype_p_v0(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()  # TODO:提交多次,需要测试
        db.delete(role)
        db.commit()
        return True
    else:
        return False
