"""
知识库管理接口
- 列表：所有登录用户可查看（对话时选择知识库）
- 新增/修改/删除：仅管理员
"""
import uuid

from flask import Blueprint, request

from extensions import db
from models.document import Document
from models.knowledge_base import KnowledgeBase
from services.rag_service import rag_service
from utils.auth import admin_required, get_current_user, login_required
from utils.response import error, success

kb_bp = Blueprint("kb", __name__)


@kb_bp.get("")
@login_required
def list_kb():
    """查询全部知识库列表"""
    kbs = KnowledgeBase.query.order_by(KnowledgeBase.id.asc()).all()
    return success([kb.to_dict() for kb in kbs])


@kb_bp.post("")
@admin_required
def create_kb():
    """
    新增知识库，并自动生成 Chroma 集合名
    请求体：name、description、icon
    """
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return error("知识库名称不能为空")

    kb = KnowledgeBase(
        name=name,
        description=body.get("description"),
        icon=body.get("icon") or "Collection",
        # Chroma 集合名只允许字母、数字、下划线等字符，因此用随机串生成
        collection_name=f"kb_{uuid.uuid4().hex[:12]}",
        create_by=get_current_user().id,
    )
    db.session.add(kb)
    db.session.commit()
    return success(kb.to_dict(), "创建成功")


@kb_bp.put("/<int:kb_id>")
@admin_required
def update_kb(kb_id):
    """
    修改知识库基本信息
    :param kb_id: 知识库ID
    """
    kb = db.session.get(KnowledgeBase, kb_id)
    if not kb:
        return error("知识库不存在")
    body = request.get_json(silent=True) or {}
    for field in ("name", "description", "icon"):
        if field in body:
            setattr(kb, field, body[field])
    db.session.commit()
    return success(kb.to_dict(), "修改成功")


@kb_bp.delete("/<int:kb_id>")
@admin_required
def delete_kb(kb_id):
    """
    删除知识库：同时删除其下所有文档记录与 Chroma 向量集合
    :param kb_id: 知识库ID
    """
    kb = db.session.get(KnowledgeBase, kb_id)
    if not kb:
        return error("知识库不存在")
    rag_service.delete_collection(kb.collection_name)
    Document.query.filter_by(kb_id=kb_id).delete()
    db.session.delete(kb)
    db.session.commit()
    return success(msg="删除成功")
