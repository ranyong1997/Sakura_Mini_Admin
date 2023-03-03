#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 16:05
# @Author  : 冉勇
# @Site    : 
# @File    : casbinrule_services.py
# @Software: PyCharm
# @desc    : Casbin Rule 服务
from sqlalchemy.orm import Session
from back.crud import user_services
from back.models.db_casbinrule_models import CasbinRule


def create_casbin_rules(db: Session, crs):
    """
    创建casbin规则,todo:可能会涉及批量添加
    :param db:
    :param crs:
    :return: 表中存在的相同数据的条目
    """
    k = 0
    for cr in crs:
        if filter_casbin_rule(db, cr):
            k += 1
        else:
            add_casbin_rule(db, cr)
    return k


def create_casbin_rule_g(db: Session, cr_g):
    """
    设置用户的权限组
    :param db:
    :param cr_g:
    :return: 存在返回1，不存在则增加数据并返回0，并添加改用户得到权限组
    """
    k = filter_casbin_rule_g(db, cr_g)
    if k:
        return k
    else:
        add_casbin_rule(db, cr_g)
        return 0


def add_casbin_rule(db: Session, casbinrule):
    """
    添加casbin规则
    :param db:
    :param casbinrule:
    :return:
    """
    db.add(casbinrule)
    db.commit()


def get_casbin_rule(db: Session):
    """
    获取casbin规则
    :param db:
    :return:
    """
    return db.query(CasbinRule).all()


def get_casbin_rule_count(db: Session):
    """
    获取casbin规则数量
    :param db:
    :return:
    """
    return db.query(CasbinRule).count()


def get_casbin_rules_by_act_key(db: Session, act_key: str):
    """
    根据act_key获取所有casbin规则
    :param db:
    :param act_key:
    :return:
    """
    return db.query(CasbinRule).filter_by(v2=act_key).all()


def get_users_by_casbinrule_role_key(db: Session, role_key):
    """
    根据role.key返回当前组的用户
    :param db:
    :param role_key:
    :return: 当前角色组的所有成员
    """
    crs = db.query(CasbinRule).filter_by(ptype='g', v1=role_key).all()
    users = []
    for cr in crs:
        user = user_services.get_user_by_username(db, cr.v0)
        users.append(user)
    return crs


def get_casbin_rules_by_role_key(db: Session, role_key):
    """
    根据role.key获取casbin规则
    :param db:
    :param role_key:
    :return: 该权限组所包括的所有权限casbinrule
    """
    return db.query(CasbinRule).filter_by(ptype='p', v0=role_key).all()


def filter_casbin_rule(db: Session, casbinrule):
    """
    查询是否存在相同的policy
    :param db:
    :param casbinrule:
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype, v0=casbinrule.v0, v1=casbinrule.v1,
                                          v2=casbinrule.v2).first()


def filter_casbin_rule_g(db: Session, casbinrule):
    """
    查询表中是否存在相同的角色role设置
    :param db:
    :param casbinrule:
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype, v0=casbinrule.v0, v1=casbinrule.v1).all()


def filter_casbin_rule_by_role_key(db: Session, role_key):
    """
    根据role_key获取角色role的权限数据，修改角色的权限是会重新添加数据
    :param db:
    :param role_key:
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype='p', v0=role_key).all()


def get_casbin_rules_by_obj_key(db: Session, obj_key):
    """
    根据obj_key获取所有casbin规则
    :param db:
    :param obj_key:
    :return:
    """
    return db.query(CasbinRule).filter_by(v1=obj_key).all()


def get_casbin_rules_by_username(db: Session, username: str):
    """
    根据用户名查询casbin规则
    :param db:
    :param username:
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype='g', v0=username).all()


def get_casbin_rules_by_ptype_p_v0(db: Session, role_key: str):
    """
    获取该角色的所有资源动作设置数据
    :param db:
    :param role_key: 根据role_key进行搜索
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype='p', v0=role_key).all()


def get_casbin_rules_by_ptype_g_v1(db: Session, role_key: str):
    """
    获取该角色的所有用户组
    :param db:
    :param role_key: 根据role_key进行搜索
    :return:
    """
    return db.query(CasbinRule).filter_by(ptype='g', v1=role_key).all()


def delete_casbin_rules(db, role_key):
    """
    批量删除casbin规则,成功返回条数，若返回0则表示没有存在的数据.
    :param db:
    :param role_key:
    :return:
    """
    crs = get_casbin_rules_by_ptype_p_v0(db, role_key)
    if len(crs) > 0:
        for cr in crs:
            db.delete(cr)
        db.commit()
        return len(crs)
    else:
        return 0


def delete_p_casbin_rules(db: Session, roles):
    """
    删除权限组的所有casbinrule
    :param db:
    :param roles:
    :return:
    """
    for r in roles:
        db.delete(r)
    db.commit()
