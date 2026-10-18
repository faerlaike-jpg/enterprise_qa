"""
用户管理接口（仅管理员）
"""
from flask import Blueprint, request

from extensions import db
from models.user import User
from utils.auth import admin_required, get_current_user
from utils.helpers import md5
from utils.response import error, page_data, success

user_bp = Blueprint("user", __name__)

# 新建用户 / 重置密码时的默认密码
DEFAULT_PASSWORD = "123456"


@user_bp.get("")
@admin_required
def list_users():
    """
    分页查询用户列表
    查询参数：page、size、keyword（账号/昵称模糊搜索）、role
    """
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "").strip()
    role = request.args.get("role", "").strip()

    query = User.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(db.or_(User.username.like(like), User.nickname.like(like)))
    if role:
        query = query.filter(User.role == role)
    pagination = query.order_by(User.id.asc()).paginate(page=page, per_page=size, error_out=False)
    return success(page_data(pagination))


@user_bp.post("")
@admin_required
def create_user():
    """
    新增用户，默认密码 123456（MD5 存储）
    请求体：username、nickname、role、department、status
    """
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    if not username:
        return error("账号不能为空")
    if User.query.filter_by(username=username).first():
        return error("账号已存在")

    user = User(
        username=username,
        password=md5(DEFAULT_PASSWORD),
        nickname=body.get("nickname") or username,
        role=body.get("role", "user"),
        department=body.get("department"),
        status=body.get("status", 1),
    )
    db.session.add(user)
    db.session.commit()
    return success(user.to_dict(), "新增成功，默认密码 123456")


@user_bp.put("/<int:user_id>")
@admin_required
def update_user(user_id):
    """
    修改用户信息
    :param user_id: 用户ID
    """
    user = db.session.get(User, user_id)
    if not user:
        return error("用户不存在")
    body = request.get_json(silent=True) or {}
    if user.id == get_current_user().id and (body.get("status") == 0 or body.get("role") == "user"):
        return error("不能禁用或降级当前登录的管理员")

    for field in ("nickname", "role", "department", "status"):
        if field in body:
            setattr(user, field, body[field])
    db.session.commit()
    return success(user.to_dict(), "修改成功")


@user_bp.put("/<int:user_id>/reset-password")
@admin_required
def reset_password(user_id):
    """
    重置用户密码为默认密码 123456
    :param user_id: 用户ID
    """
    user = db.session.get(User, user_id)
    if not user:
        return error("用户不存在")
    user.password = md5(DEFAULT_PASSWORD)
    db.session.commit()
    return success(msg="密码已重置为 123456")


@user_bp.delete("/<int:user_id>")
@admin_required
def delete_user(user_id):
    """
    删除用户
    :param user_id: 用户ID
    """
    if user_id == get_current_user().id:
        return error("不能删除当前登录的账号")
    user = db.session.get(User, user_id)
    if not user:
        return error("用户不存在")
    db.session.delete(user)
    db.session.commit()
    return success(msg="删除成功")
