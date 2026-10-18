"""
知识库文档模型
"""
from datetime import datetime

from extensions import db
from utils.helpers import fmt_time


class Document(db.Model):
    """知识库文档表 kb_document，记录上传文件及其向量化状态"""

    __tablename__ = "kb_document"

    # 文档处理状态常量
    STATUS_PENDING = 0   # 待处理
    STATUS_DONE = 1      # 已完成
    STATUS_FAILED = 2    # 失败

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    kb_id = db.Column(db.Integer, nullable=False, index=True, comment="知识库ID")
    file_name = db.Column(db.String(255), nullable=False, comment="原始文件名")
    file_path = db.Column(db.String(500), nullable=False, comment="存储路径")
    file_type = db.Column(db.String(20), nullable=False, comment="文件类型")
    file_size = db.Column(db.BigInteger, default=0, comment="文件大小")
    chunk_count = db.Column(db.Integer, default=0, comment="切分片段数")
    status = db.Column(db.SmallInteger, default=STATUS_PENDING, comment="状态")
    error_msg = db.Column(db.String(500), comment="失败原因")
    upload_by = db.Column(db.Integer, comment="上传人ID")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="上传时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "kb_id": self.kb_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "chunk_count": self.chunk_count,
            "status": self.status,
            "error_msg": self.error_msg,
            "upload_by": self.upload_by,
            "create_time": fmt_time(self.create_time),
        }
