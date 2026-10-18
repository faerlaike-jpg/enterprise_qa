"""
企业内部知识库问答 Agent 系统 - 后端启动入口
使用应用工厂模式创建 Flask 应用
"""
import os

from flask import Flask

from config import Config
from extensions import cors, db, jwt
from utils.response import error, success


def register_blueprints(app):
    """
    注册所有路由蓝图
    :param app: Flask 应用实例
    """
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.kb import kb_bp
    from routes.document import doc_bp
    from routes.chat import chat_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(kb_bp, url_prefix="/api/kb")
    app.register_blueprint(doc_bp, url_prefix="/api/documents")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")


def register_jwt_handlers():
    """注册 JWT 异常回调，统一返回 JSON 格式的 401 错误"""

    @jwt.unauthorized_loader
    def missing_token(reason):
        """请求未携带 Token"""
        return error("请先登录", 401, 401)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        """Token 无效"""
        return error("登录凭证无效，请重新登录", 401, 401)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        """Token 已过期"""
        return error("登录已过期，请重新登录", 401, 401)


def create_app():
    """
    应用工厂函数
    :return: 配置完成的 Flask 应用实例
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    # 确保上传目录与向量库目录存在
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.CHROMA_DIR, exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    register_jwt_handlers()
    register_blueprints(app)

    @app.route("/api/health")
    def health():
        """健康检查接口"""
        return success({"status": "ok"})

    @app.errorhandler(413)
    def too_large(e):
        """上传文件过大"""
        return error("文件大小超过 20MB 限制", 413, 413)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
