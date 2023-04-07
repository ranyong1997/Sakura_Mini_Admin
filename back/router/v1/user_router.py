#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 11:31
# @Author  : 冉勇
# @Site    : 
# @File    : user_router.py
# @Software: PyCharm
# @desc    : 用户路由
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from back.app.config import Config
from back.dbdriver.mysql import get_db
from back.schemas import user_schemas
from back.schemas.user_schemas import User, Casbin_rule, Users, UserUpdate, ChangeUserRole, Token, \
    ResetPassword
from back.utils.exception.errors import TokenAuthError
from back.utils.password import get_password_hash
from back.dbdriver.redis import redis_client
from back.utils.response.response_schema import response_base
from back.utils.token import oauth2_scheme, get_username_by_token
from back.utils.casbin import verify_enforce
from back.crud import user_services, role_services, casbinrule_services

router = APIRouter(
    prefix="/v1",
    tags=["用户"],
    responses={404: {"description": "Not Found"}}  # 请求异常返回数据
)

no_permission = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    # TODO:后续封装所有请求结果
    detail="您没有该权限",
    headers={"WWW-Authenticate": "Bearer"}
)


def return_rule(obj, act):
    """
    返回一个验证权限的规则，包括obj、act。
    """
    return Casbin_rule(obj=obj, act=act)


################################
# User相关的api接口
################################
@router.post("/user/create_user", summary="创建用户")
async def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    创建用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名称重复",
        headers={"WWW-Authenticate": "Bearer"}
    )
    # 注册用户名称不能与用户组的role_key重复
    role = role_services.get_role_by_role_key(db, user.username)
    if role:
        raise credentials_exception
    return user_services.create_user(db, user.username, user.password, user.sex, user.email)


@router.get("/user/me", response_model=User, summary="返回当前用户的资料")
async def read_user_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    返回当前用户的资料
    """
    username = get_username_by_token(token)
    return user_services.get_user_by_username(db, username)


@router.get("/user/user_by_id", response_model=User, summary="根据id获取用户资料")
async def get_user_by_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    根据id获取用户资料
    """
    if verify_enforce(token, return_rule("User", "read")):
        return user_services.get_user_by_id(db, user_id)
    else:
        raise no_permission


@router.get("/user/get_users", response_model=Users, summary="获取用户")
async def get_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 10,
                    keyword: str = ""):
    """
    获取用户
    """
    users = Users(users=user_services.get_users(db, skip, limit, keyword),
                  count=user_services.get_users_count_by_keyword(db, keyword))
    return users


@router.get("/users/active_change", summary="修改用户锁定")
async def user_active_change(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    修改用户锁定
    """
    if verify_enforce(token, return_rule('User', 'update')):
        return user_services.active_change(db, user_id)
    else:
        raise no_permission


@router.delete("/user/delete_user", summary="根据id删除用户")
async def delete_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    根据id删除用户
    """
    if verify_enforce(token, return_rule("User", "delete")):
        return user_services.delete_user_by_id(db, user_id)
    else:
        raise no_permission


@router.post("/user/update_user", summary="修改用户资料")
async def update_user(user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户资料
    """
    if verify_enforce(token, return_rule("User", "update")):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名称重复!",
            headers={"WWW-Authenticate": "Bearer"}
        )
        u = user_services.get_user_by_id(db, user.user_id)
        # 修改用户名称不能与用户组的role_key重复
        role = role_services.get_role_by_role_key(db, user.username)
        if role:
            raise credentials_exception
        u.username = user.username
        u.sex = user.sex
        u.remark = user.remark
        u.avatar = user.avatar
        if user.password != "":
            hashed_password = get_password_hash(user.password)
            u.hashed_password = hashed_password
        try:
            db.commit()
            return True
        except:
            return False
    else:
        raise no_permission


@router.post("/user/update_me", summary="修改用户资料")
async def update_me(user: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户资料
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据!",
        headers={"WWW-Authenticate": "Bearer"}
    )
    username = get_username_by_token(token)
    me = user_services.get_user_by_username(db, username)
    # bug:获取不到id
    if user.user_id == me.id:
        u = user_services.get_user_by_id(db, user.user_id)
        u.username = user.username
        u.email = user.email
        u.sex = user.sex
        u.avatar = user.avatar
        if user.password != "":
            hashed_password = get_password_hash(user.password)
            u.hashed_password = hashed_password
        try:
            db.commit()
            return True
        except:
            raise credentials_exception
    else:
        return no_permission


@router.post("/user/change_user_role", summary="修改用户拥有的用户组")
async def change_user_role(data: ChangeUserRole, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户拥有的用户组
    """
    if verify_enforce(token, return_rule('User', 'update')):
        # 将用户组名称改成role_key
        role_keys = []
        for name in data.names:
            role = role_services.get_role_by_name(db, name)
            role_keys.append(role.role_key)
        return user_services.change_user_role(db, data.user_id, role_keys)
    else:
        raise no_permission


@router.get("/user/get_user_role", summary="获取用户所拥有的用户组")
async def get_user_role(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取用户所拥有的用户组
    """
    if verify_enforce(token, return_rule("User", "read")):
        user = user_services.get_user_by_id(db, user_id)
        roles = role_services.get_roles(db)
        options = []  # 所有权限组名称
        for role in roles:
            options.append(role.name)
        checkeds = []  # 当前用户所拥有的用户组
        crs = casbinrule_services.get_casbin_rules_by_username(db, user.username)
        for cr in crs:
            role = role_services.get_role_by_role_key(db, cr.v1)
            checkeds.append(role.name)
        return {'options': options, 'checkeds': checkeds}
    else:
        raise no_permission


@router.post('/user/login', summary='用户登录', response_model=Token, description='用户登录')
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token, is_super = await user_services.login(form_data)
    return Token(access_token=token, is_superuser=is_super, msg="🎊🎊登录成功")


@router.post("/user/logout", summary='用户退出')
async def user_logout(token: str = Depends(oauth2_scheme)):
    """
    用户退出
    """
    username = get_username_by_token(token)  # token中获取用户名
    if not username:
        raise TokenAuthError
    else:
        # 2、拿到username后传入到redis的key中,并将该token删除
        await redis_client.delete(f'{Config.REDIS_PREFIX}:user:{username}')
    return response_base.response_200(msg='退出登录成功')


@router.post('/password/reset/captcha', summary='获取密码重置验证码')
def password_reset_captcha(username_or_email: str, response: Response):
    """
    可以通过用户名或者邮箱重置密码
    """
    user_services.get_pwd_rest_captcha(username_or_email=username_or_email, response=response)
    return response_base.response_200(msg='验证码发送成功')


@router.post('/password/reset', summary='密码重置请求')
def password_reset(obj: ResetPassword, request: Request, response: Response):
    """
    密码重置
    """
    user_services.pwd_reset(obj=obj, request=request, response=response)
    return response_base.response_200(msg='密码重置成功')


@router.get('/password/reset/done', summary='重置密码完成')
def password_reset_done():
    """
    重置密码完成
    """
    return response_base.response_200(msg='重置密码完成')


@router.put('/user/{username}/avatar', summary='更新头像')
def update_avatar(username: str, avatar: UploadFile, current_user: User = Depends(oauth2_scheme)):
    """
    更新用户头像
    """
    count = user_services.update_avatar(username=username, avatar=avatar, current_user=current_user)
    if count > 0:
        return response_base.response_200(msg='更新头像成功')
    return response_base.fail()


@router.delete('/user/{username}/avater', summary='删除头像文件')
def delete_avater(username: str, current_user: User = Depends(oauth2_scheme)):
    """
    删除用户头像文件
    """
    count = user_services.delete_avatar(username=username, current_user=current_user)
    if count > 0:
        return response_base.response_200(msg='删除用户头像成功')
    return response_base.fail()
