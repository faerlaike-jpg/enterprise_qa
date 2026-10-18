"""
鉴权相关工具：获取当前登录用户、管理员权限装饰器
"""
from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from extensions import db
from models.user import User
from utils.response import error


def get_current_user():
    """
    根据 JWT 中的身份标识获取当前登录用户
    :return: User 对象或 None
    """
    identity = get_jwt_identity()
    if identity is None:
        return None
    return db.session.get(User, int(identity))


def login_required(fn):
    """登录校验装饰器：要求请求携带有效 Token，且用户状态正常"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if not user or user.status != 1:
            return error("用户不存在或已被禁用", 401, 401)
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """管理员权限装饰器：要求当前用户角色为 admin"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if not user or user.status != 1:
            return error("用户不存在或已被禁用", 401, 401)
        if not user.is_admin:
            return error("无权限访问，需要管理员角色", 403, 403)
        return fn(*args, **kwargs)

    return wrapper
