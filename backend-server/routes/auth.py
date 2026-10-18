"""
认证接口：登录、获取当前用户信息、修改密码
"""
from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from extensions import db
from models.user import User
from utils.auth import get_current_user, login_required
from utils.response import error, success

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """
    用户登录
    请求体：{"username": "admin", "password": "<前端MD5后的密码>"}
    返回：token 与用户信息
    """
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip().lower()
    if not username or not password:
        return error("用户名和密码不能为空")

    user = User.query.filter_by(username=username).first()
    # 前端已对明文做 MD5，这里直接与数据库中的 MD5 值比对
    if not user or user.password != password:
        return error("用户名或密码错误")
    if user.status != 1:
        return error("账号已被禁用，请联系管理员")

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return success({"token": token, "user": user.to_dict()}, "登录成功")


@auth_bp.get("/info")
@login_required
def info():
    """获取当前登录用户信息"""
    return success(get_current_user().to_dict())


@auth_bp.put("/password")
@login_required
def change_password():
    """
    修改当前用户密码
    请求体：{"old_password": "<MD5>", "new_password": "<MD5>"}
    """
    body = request.get_json(silent=True) or {}
    user = get_current_user()
    if user.password != (body.get("old_password") or "").lower():
        return error("原密码错误")
    new_password = (body.get("new_password") or "").lower()
    if len(new_password) != 32:
        return error("新密码格式不正确")
    user.password = new_password
    db.session.commit()
    return success(msg="密码修改成功")
