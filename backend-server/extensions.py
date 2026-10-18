"""
Flask 扩展实例集中管理
单独放在一个模块中，避免模型与应用之间的循环导入
"""
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# ORM 数据库实例
db = SQLAlchemy()

# JWT 鉴权实例
jwt = JWTManager()

# 跨域实例
cors = CORS()
