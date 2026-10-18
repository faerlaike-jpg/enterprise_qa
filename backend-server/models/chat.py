"""
对话相关模型：会话、消息、反馈
"""
from datetime import datetime

from extensions import db
from utils.helpers import fmt_time


class ChatSession(db.Model):
    """对话会话表 chat_session，一个会话包含多条消息"""

    __tablename__ = "chat_session"

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    user_id = db.Column(db.Integer, nullable=False, index=True, comment="用户ID")
    kb_id = db.Column(db.Integer, comment="知识库ID")
    title = db.Column(db.String(200), default="新对话", comment="会话标题")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "kb_id": self.kb_id,
            "title": self.title,
            "create_time": fmt_time(self.create_time),
            "update_time": fmt_time(self.update_time),
        }


class ChatMessage(db.Model):
    """对话消息表 chat_message，role 为 user 或 assistant"""

    __tablename__ = "chat_message"

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    session_id = db.Column(db.Integer, nullable=False, index=True, comment="会话ID")
    role = db.Column(db.String(20), nullable=False, comment="角色")
    content = db.Column(db.Text(length=4294967295), nullable=False, comment="消息内容")
    sources = db.Column(db.JSON, comment="引用来源")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "sources": self.sources or [],
            "create_time": fmt_time(self.create_time),
        }


class Feedback(db.Model):
    """回答反馈表 feedback，记录用户对 AI 回答的点赞/点踩"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    message_id = db.Column(db.Integer, nullable=False, comment="消息ID")
    user_id = db.Column(db.Integer, nullable=False, comment="用户ID")
    type = db.Column(db.SmallInteger, nullable=False, comment="1点赞 -1点踩")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
