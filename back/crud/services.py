#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 15:50
# @Author  : 冉勇
# @Site    : 
# @File    : services.py
# @Software: PyCharm
# @desc    : CRUD接口
import os
import random
from _xxsubinterpreters import get_current
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional
from email_validator import validate_email, EmailNotValidError
from fast_captcha import text_captcha
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request, Response, HTTPException, Depends, UploadFile
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from starlette import status

from back.app import settings
from back.app.database import SessionLocal, get_db
from back.crud import user_services
from back.models.db_casbin_object_models import CasbinObject
from back.models.db_casbinaction_models import CasbinAction
from back.models.db_casbinrule_models import CasbinRule
from back.models.db_role_models import Role
from back.models.db_user_models import User
from back.router.v1.token_router import authenticate_user
from back.schemas.user_schemas import ResetPassword
from back.utils import password, token
from back.utils.exception import errors
from back.utils.generate_string import get_current_timestamp
from back.utils.password import get_password_hash, verify_password
from back.utils.logger import log
from back.utils.redis import redis_client
from back.utils.send_email import send_verification_code_email
from back.utils.token import APP_TOKEN_CONFIG, create_access_token


# TODO:后续将每个crud分离出来
def create_data(db: Session):
    """
    添加超管和一些普通用户
    :param db:
    :return:
    """
    # 创建超管
    hashed_password = get_password_hash('123456')
    if not get_user_by_username(db, "root"):
        add_user(db, User(username='root', hashed_password=hashed_password, email='root@example.com', is_active=False,
                          is_superuser=True, remark='超级管理员，拥有所有权限'))
        log.info("创建超级管理员：root")
    user = get_user_by_username(db, "root")
    if get_role_count(db) <= 0:
        create_role(db, Role(name='超级管理员', role_key='role_superadmin', description='超级管理员，拥有所有系统的权限',
                             user=user))
        create_role(db, Role(name='管理员', role_key='role_admin', description='管理员', user=user))
        create_role(db, Role(name='普通用户', role_key='role_generaluser', description='默认注册的用户', user=user))
    # 如果casbin行为<=0,则创建CasbinAction
    if get_casbin_action_count(db) <= 0:
        # 创建CasbinAction
        cas = [
            CasbinAction(name='增', action_key='create', description='增加数据', user=user),
            CasbinAction(name='删', action_key='delete', description='删除数据', user=user),
            CasbinAction(name='改', action_key='update', description='更新数据', user=user),
            CasbinAction(name='查', action_key='read', description='读取或查询数据', user=user),
            CasbinAction(name='显', action_key='show', description='数据相关组件的显示', user=user)
        ]
        add_casbin_action(db, cas)
    # 如果casbin项目<=0,则创建CasbinObject
    if get_casbin_object_count(db) <= 0:
        # 创建CasbinObject
        cos = [
            CasbinObject(name='用户管理', object_key='User', description='User表--用户相关权限', user=user),
            CasbinObject(name='角色管理', object_key='Role', description='Role表--角色相关权限', user=user),
            CasbinObject(name='资源管理', object_key='CasbinObject', description='CasbinObject--资源相关权限',
                         user=user),
            CasbinObject(name='动作管理', object_key='CasbinAction', description='CasbinAction--用户相关权限',
                         user=user)
        ]
        add_casbin_objects(db, cos)
        log.info("创建用户管理、角色管理、资源管理、动作管理")
    # 如果casbin规则<=0,则创建CasbinRule
    if get_casbin_rule_count(db) <= 0:
        # 创建CasbinRule
        log.info("设置用户组权限")
        set_user_role(db)
        log.info("设置超级管理员")
        role_superadmin = get_role_by_id(db, 1)  # 超级管理员
        create_casbin_rule_g(db, CasbinRule(ptype='g', v0=user.username, v1=role_superadmin.role_key))
        log.info("生成一些普通用户")
        create_temp_users(db)


# --------------------------【User增删改查】--------------------------------------
def pwd_reset(*, obj: ResetPassword, request: Request, response: Response):
    """
    密码重置
    :param obj:
    :param request:
    :param response:
    :return:
    """
    with SessionLocal.begin() as db:
        pwd1 = obj.password1
        pwd2 = obj.password2
        cookie_reset_pwd_code = request.cookies.get('fastapi_reset_pwd_code')
        cookie_reset_pwd_username = request.cookies.get('fastapi_reset_pwd_username')
        if pwd1 != pwd2:
            raise errors.ForbiddenError(msg='两次密码输入不一致')
        if cookie_reset_pwd_username is None or cookie_reset_pwd_code is None:
            raise errors.NotFoundError(msg='验证码已失效，请重新获取验证码')
        if cookie_reset_pwd_code != sha256(obj.code.encode('utf-8')).hexdigest():
            raise errors.ForbiddenError(msg='验证码错误')
        reset_password(db, cookie_reset_pwd_username, obj.password2)
        response.delete_cookie(key='fastapi_reset_pwd_code')
        response.delete_cookie(key='fastapi_reset_pwd_username')


def get_pwd_rest_captcha(*, username_or_email: str, response: Response):
    """
    获取验证码
    :param username_or_email:
    :param response:
    :return:
    """
    with SessionLocal.begin() as db:
        code = text_captcha()
        if get_user_by_username(db, username_or_email):
            try:
                response.delete_cookie(key='fastapi_reset_pwd_code')
                response.delete_cookie(key='fastapi_reset_pwd_username')
                response.set_cookie(
                    key='fastapi_reset_pwd_code',
                    value=sha256(code.encode('utf-8')).hexdigest(),
                    max_age=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
                )
                response.set_cookie(
                    key='fastapi_reset_pwd_username',
                    value=username_or_email,
                    max_age=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            except Exception as e:
                log.exception('无法发送验证码 {}', e)
                raise e
            current_user_email = get_email_by_username(db, username_or_email)
            send_verification_code_email(current_user_email, code)
        else:
            try:
                validate_email(username_or_email, check_deliverability=False)
            except EmailNotValidError as e:
                raise HTTPException(status_code=404, detail='用户名不存在') from e
            email_result = check_email(db, username_or_email)
            if not email_result:
                raise HTTPException(status_code=404, detail='邮箱不存在')
            try:
                response.delete_cookie(key='fastapi_reset_pwd_code')
                response.delete_cookie(key='fastapi_reset_pwd_username')
                response.set_cookie(
                    key='fastapi_reset_pwd_code',
                    value=sha256(code.encode('utf-8')).hexdigest(),
                    max_age=settings.COOKIES_MAX_AGE
                )
                username = get_username_by_email(db, username_or_email)
                response.set_cookie(
                    key='fastapi_reset_pwd_username',
                    value=username,
                    max_age=settings.COOKIES_MAX_AGE
                )
            except Exception as e:
                log.exception('无法发送验证码 {}', e)
                raise e
            send_verification_code_email(username_or_email, code)


def create_user(db: Session, username: str, password: str, sex: str, email: str):
    """
    创建一个用户
    :param db:
    :param username: 用户名
    :param password: 密码
    :param sex: 性别
    :param email: 邮箱
    :return: Boolean
    """
    role_user = get_role_by_id(db, 3)  # 普通用户组
    hashed_password = get_password_hash(password)
    user = User()
    user.username = username
    user.hashed_password = hashed_password
    user.email = email
    user.sex = sex
    user = add_user(db, user)
    create_casbin_rule_g(db, CasbinRule(ptype='g', v0=user.username, v1=role_user.role_key))  # 添加普通用户权限
    return True


def set_user_role(db: Session):
    """
    设置超级管理员组合普通用户组权限
    :param db:
    :return:
    """
    role_superadmin = get_role_by_id(db, 1)  # 超管
    cas = get_casbin_actions(db)  # 所有行为
    cos = get_casbin_objects(db)  # 所有资源
    crs = []
    for co in cos:
        for ca in cas:
            crs.append(CasbinRule(ptype='p', v0=role_superadmin.role_key, v1=co.object_key, v2=ca.action_key))
    # 为超管增加所有的policy
    create_casbin_rules(db, crs)
    role_user = get_role_by_id(db, 3)  # 普通用户
    cos = get_casbin_objects(db)  # 所有资源
    cas1 = ['read', 'show']  # 仅读、显权限
    crs1 = []
    for co in cos:
        for ca in cas1:
            crs1.append(CasbinRule(ptype='p', v0=role_user.role_key, v1=co.object_key, v2=ca))
    # 为普通用户增加所有policy
    create_casbin_rules(db, crs1)


def check_email(db: Session, email: str) -> Optional[User]:
    """
    检查邮箱
    :param db:
    :param email:
    :return:
    """
    return db.execute(select(User).where(User.email == email)).scalars().first()


def create_temp_users(db: Session):
    """
    随机添加0~10个测试用户,并添加普通用户组权限
    todo:上线则注释该代码
    :param db:
    :return:
    """
    # 添加一些用户
    hashed_password = get_password_hash('123456')
    role_user = get_role_by_id(db, 3)  # 普通用户组
    if get_users_count(db) <= 1:
        for i in range(10):
            sex = str(random.randint(0, 1))
            is_active = False
            if random.randint(0, 1): is_active = True
            k = str(i)
            u = User(username='mini' + k, hashed_password=hashed_password, email='admin' + k + '@example.com',
                     sex=sex, is_active=is_active, remark='临时测试用户')
            user = add_user(db, u)
            create_casbin_rule_g(db, CasbinRule(ptype='g', v0=user.username, v1=role_user.role_key))


def get_users(db: Session, offset: int, limit: int, keyword: str):
    """
    获取用户
    支持模糊查询
    :param db:
    :param offset:
    :param limit:
    :param keyword:
    :return:
    """
    return db.query(User).order_by(User.id).filter(User.username.like(f"%{keyword}%")).offset(offset).limit(
        limit).all()


def get_user_by_id(db: Session, id: int):
    """
    根据id获取用户
    :param db:
    :param id:
    :return:
    """
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str):
    """
    根据用户名获取用户
    :param db:
    :param username:
    :return:
    """
    return db.query(User).filter_by(username=username).first()


def get_admin_by_username(db: Session, username: str):
    """
    根据用户名获取管理员
    :param db:
    :param username:
    :return:
    """
    return db.query(User).filter(User.is_superuser == username).first()


def get_users_count_by_keyword(db: Session, keyword: str):
    """
    关键字查询用户
    :param db:
    :param keyword:
    :return:
    """
    return db.query(User).filter(User.username.like(f"%{keyword}%")).count()


def active_change(db: Session, user_id):
    """
    修改用户锁定
    :param db:
    :param user_id:
    :return:
    """
    if user := get_user_by_id(db, user_id):
        user.is_active = not user.is_active
        db.commit()
        return True
    else:
        return False


def change_user_password(db: Session, old_password: str, new_password: str, user_id: int):
    """
    修改密码
    :param db:
    :param old_password: 旧密码
    :param new_password: 新密码
    :param user_id: 用户id
    :return:
    """
    user = get_user_by_id(db, user_id)
    if verify_password(old_password, user.hashed_password):
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
    else:
        return False


def change_user_role(db: Session, user_id: int, role_keys: list):
    """
    改变用户所属的用户组
    :param db:
    :param user_id:
    :param role_key:
    :return:
    """
    user = db.query(User).filter_by(id=user_id).first()
    crs = db.query(CasbinRule).filter_by(ptype='g', v0=user.username).all()
    if len(crs) > 0:
        delete_p_casbin_rules(db, crs)  # 删除该用户所拥有的用户组role
    new_crs = []
    for role_key in role_keys:
        new_crs.append(CasbinRule(ptype='g', v0=user.username, v1=role_key))
    try:
        create_casbin_rules(db, new_crs)
        return True
    except Exception:
        return False


def delete_user_by_id(db: Session, user_id: int):
    """
    根据id删除用户
    :param db:
    :param user_id:
    :return:
    """
    try:
        user = db.query(User).filter_by(id=user_id).first()
        crs = get_casbin_rules_by_username(db, user.username)
        for cr in crs:
            db.delete(cr)
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        return False


def update_user_login_time(db: Session, username: str) -> int:
    """
    更新用户登录时间
    :param db:
    :param username:
    :return:
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        user.last_login = datetime.now()
        db.commit()
        return True
    except Exception:
        return False


def get_email_by_username(db: Session, username: str) -> str:
    """
    通过邮箱获取用户名
    :param db:
    :param username:
    :return:
    """
    return get_user_by_username(db, username).email


def get_username_by_email(db: Session, email: str) -> str:
    """
    通过用户名获得邮箱
    :param db:
    :param email:
    :return:
    """
    return db.execute(select(User).where(User.email == email)).scalars().first().username


def reset_password(db: Session, username: str, password: str) -> int:
    """
    重置密码
    :param db:
    :param username:
    :param password:
    :return:
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        user.hashed_password = get_password_hash(password)
        db.commit()
        return True
    except Exception:
        return False


def update_avatar(*, username: str, avatar: UploadFile):
    with SessionLocal.begin() as db:
        input_user = get_user_by_username(db, username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        input_user_avatar = input_user.avatar
        if avatar is not None:
            if input_user_avatar is not None:
                try:
                    os.remove(settings.AvatarPath + input_user_avatar)
                except Exception as e:
                    log.error(f'用户 {username} 更新头像时，原头像文件 {input_user_avatar} 删除失败\n{e}')
            new_file = avatar.file.read()
            if 'image' not in avatar.content_type:
                raise errors.ForbiddenError(msg='图片格式错误，请重新选择图片')
            file_name = f'{str(get_current_timestamp())}_{avatar.filename}'
            if not os.path.exists(settings.AvatarPath):
                os.makedirs(settings.AvatarPath)
            with open(f'{settings.AvatarPath}{file_name}', 'wb') as f:
                f.write(new_file)
        else:
            file_name = input_user_avatar
        return user_services.update_avatar(db, input_user, file_name)


# --------------------------【User增删改查 完】--------------------------------------


# --------------------------【Role增删改查】--------------------------------------
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


# --------------------------【Role增删改查 完】--------------------------------------

# --------------------------【CasbinAction增删改查】--------------------------------------
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


# --------------------------【CasbinAction增删改查 完】--------------------------------------

# --------------------------【CasbinObject增删改查】--------------------------------------
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


# --------------------------【CasbinObject增删改查 完】--------------------------------------

# --------------------------【CasbinRulet增删改查】--------------------------------------
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
        user = get_user_by_username(db, cr.v0)
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
# --------------------------【CasbinRulet增删改查 完】--------------------------------------
