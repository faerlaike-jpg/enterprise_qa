"""
系统配置模块
从 .env 文件读取数据库、JWT、大模型、向量库等配置项
"""
import os
from datetime import timedelta

from dotenv import load_dotenv

# 项目根目录（backend-server）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载 .env 环境变量
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """全局配置类，Flask 通过 app.config.from_object(Config) 加载"""

    # ---------- 数据库 ----------
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DB = os.getenv("MYSQL_DB", "db_enterprise_qa")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 3600}

    # ---------- JWT ----------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "enterprise-qa-jwt-secret-key-please-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "24")))

    # ---------- 上传 ----------
    UPLOAD_DIR = os.path.join(BASE_DIR, os.getenv("UPLOAD_DIR", "uploads"))
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 单文件最大 20MB
    ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx"}

    # ---------- 大模型 DeepSeek ----------
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    # ---------- 嵌入模型 阿里云百炼 ----------
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3.7-text-embedding-flash")

    # ---------- RAG 参数 ----------
    CHROMA_DIR = os.path.join(BASE_DIR, os.getenv("CHROMA_DIR", "chroma_data"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K = int(os.getenv("TOP_K", "4"))
    AGENT_MODE = os.getenv("AGENT_MODE", "true").lower() == "true"
