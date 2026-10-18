"""
知识库模型
"""
from datetime import datetime

from extensions import db
from utils.helpers import fmt_time


class KnowledgeBase(db.Model):
    """知识库表 knowledge_base，每个知识库对应 Chroma 中的一个 collection"""

    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True, comment="主键ID")
    name = db.Column(db.String(100), nullable=False, comment="知识库名称")
    description = db.Column(db.String(500), comment="描述")
    collection_name = db.Column(db.String(63), unique=True, nullable=False, comment="Chroma集合名")
    icon = db.Column(db.String(50), default="Collection", comment="图标")
    doc_count = db.Column(db.Integer, default=0, comment="文档数量")
    create_by = db.Column(db.Integer, comment="创建人ID")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "collection_name": self.collection_name,
            "icon": self.icon,
            "doc_count": self.doc_count,
            "create_by": self.create_by,
            "create_time": fmt_time(self.create_time),
        }
