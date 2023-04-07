#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/28 15:30
# @Author  : 冉勇
# @Site    : 
# @File    : user_services.py
# @Software: PyCharm
# @desc    : 用户服务
import os
import random
from datetime import timedelta, datetime
from hashlib import sha256
from typing import Optional
from email_validator import validate_email, EmailNotValidError
from fast_captcha import text_captcha
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update, select
from sqlalchemy.orm import Session
from back.app import settings
from back.crud import role_services
from back.dbdriver.mysql import SessionLocal
from back.crud.casbinaction_services import get_casbin_action_count, add_casbin_action, get_casbin_actions
from back.crud.casbinobject_services import get_casbin_object_count, add_casbin_objects, get_casbin_objects
from back.crud.casbinrule_services import get_casbin_rule_count, create_casbin_rule_g, create_casbin_rules, \
    delete_p_casbin_rules, get_casbin_rules_by_username
from back.crud.role_services import add_user, get_role_count, get_users_count, get_role_by_id
from back.models.db_casbin_object_models import CasbinObject
from back.models.db_casbinaction_models import CasbinAction
from back.models.db_casbinrule_models import CasbinRule
from back.models.db_role_models import Role
from back.models.db_user_models import User
from back.router.v1.role_router import create_role
from back.schemas.user_schemas import ResetPassword
from back.utils import password, token
from back.utils.exception import errors
from back.utils.generate_string import get_current_timestamp
from back.utils.logger import log
from back.utils.password import get_password_hash, verify_password
from back.dbdriver.redis import redis_client
from back.utils.send_email import send_verification_code_email
from back.utils.token import APP_TOKEN_CONFIG
from fastapi import Request, Response, HTTPException, UploadFile


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
        role_services.create_role(db, Role(name='超级管理员', role_key='role_superadmin',
                                           description='超级管理员，拥有所有系统的权限', user=user))
        role_services.create_role(db, Role(name='管理员', role_key='role_admin', description='管理员', user=user))
        role_services.create_role(db, Role(name='普通用户', role_key='role_generaluser', description='默认注册的用户',
                                           user=user))
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


async def login(form_data: OAuth2PasswordRequestForm):
    with SessionLocal() as db:
        current_user = get_user_by_username(db, form_data.username)
        if not current_user:
            raise errors.NotFoundError(msg='用户名不存在')
        elif not password.verity_password(form_data.password, current_user.hashed_password):
            raise errors.AuthorizationError(msg='密码错误')
        elif current_user.is_active:
            raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
        # 更新登陆时间
        update_user_login_time(db, form_data.username)
        # 创建token
        access_token_expired = timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
        # token过期时间
        access_token = token.create_access_token(data={'sub': form_data.username}, expires_delta=access_token_expired)
        # 将token写入redis,并设置过期销毁时间,创建根目录/Sakura/user
        await redis_client.set(f'{settings.REDIS_PREFIX}:user:{form_data.username}', access_token,
                               ex=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
        return access_token, current_user.is_superuser


def Update_avatar(db: Session, current_user: User, avatar: str):
    """
    更新头像
    :param db:
    :param current_user:
    :param avatar:
    :return:
    """
    user = db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=avatar)
    )
    return user.rowcount


def Delete_avatar(db: Session, user_id: int) -> int:
    """
    删除头像
    :param db:
    :param user_id:
    :return:
    """
    user = db.execute(
        update(User)
        .where(User.id == user_id)
        .values(avatar=None)
    )
    return user.rowcount


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
    return [{"msg": "用户创建成功", "用户名": user.username, "邮箱:": user.email}]


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
    :param role_keys:
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


def update_avatar(*, username: str, avatar: UploadFile, current_user: User):
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
        return Update_avatar(db, input_user, file_name)


def delete_avatar(*, username: str, current_user: User):
    with SessionLocal.begin() as db:
        input_user = get_user_by_username(db, username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        input_user_avatar = input_user.avatar
        if input_user_avatar is not None:
            try:
                os.remove(settings.AvatarPath + input_user_avatar)
            except Exception as e:
                log.error(f'用户 {input_user.username} 删除头像文件 {input_user_avatar} 失败\n{e}')
        else:
            raise errors.NotFoundError(msg='用户没有头像文件，请上传头像文件后再执行此操作')
        return Delete_avatar(db, input_user.id)
