"""
用户模型
"""
from datetime import datetime

from extensions import db
from utils.helpers import fmt_time


class User(db.Model):
    """系统用户表 sys_user，区分管理员(admin)与普通用户(user)两种角色"""

    __tablename__ = "sys_user"

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    username = db.Column(db.String(50), unique=True, nullable=False, comment="登录账号")
    password = db.Column(db.String(64), nullable=False, comment="登录密码(MD5)")
    nickname = db.Column(db.String(50), comment="昵称")
    role = db.Column(db.String(20), nullable=False, default="user", comment="角色")
    avatar = db.Column(db.String(255), comment="头像")
    department = db.Column(db.String(50), comment="部门")
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment="状态 1正常 0禁用")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    @property
    def is_admin(self):
        """判断当前用户是否为管理员"""
        return self.role == "admin"

    def to_dict(self):
        """转换为字典（不包含密码字段）"""
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
            "avatar": self.avatar,
            "department": self.department,
            "status": self.status,
            "create_time": fmt_time(self.create_time),
        }
