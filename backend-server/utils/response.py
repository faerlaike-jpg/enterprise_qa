"""
统一接口返回格式
所有接口返回结构：{"code": 200, "msg": "success", "data": ...}
"""
from flask import jsonify


def success(data=None, msg="success"):
    """
    成功响应
    :param data: 返回数据
    :param msg: 提示信息
    """
    return jsonify({"code": 200, "msg": msg, "data": data})


def error(msg="error", code=400, http_status=200):
    """
    失败响应
    :param msg: 错误信息
    :param code: 业务错误码
    :param http_status: HTTP 状态码（默认 200，前端统一按 code 判断）
    """
    return jsonify({"code": code, "msg": msg, "data": None}), http_status


def page_data(pagination):
    """
    将 Flask-SQLAlchemy 分页对象转换为统一分页结构
    :param pagination: db.paginate 返回的分页对象
    """
    return {
        "list": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "size": pagination.per_page,
    }
