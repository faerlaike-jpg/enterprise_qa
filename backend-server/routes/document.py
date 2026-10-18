"""
知识库文档管理接口（仅管理员）
上传文档后会同步执行：加载 -> 切分 -> 向量化 -> 写入 Chroma
"""
import os
import uuid

from flask import Blueprint, request

from config import BASE_DIR, Config
from extensions import db
from models.document import Document
from models.knowledge_base import KnowledgeBase
from services.rag_service import rag_service
from utils.auth import admin_required, get_current_user
from utils.response import error, page_data, success

doc_bp = Blueprint("document", __name__)


def refresh_doc_count(kb_id):
    """
    重新统计知识库下的文档数量
    :param kb_id: 知识库ID
    """
    kb = db.session.get(KnowledgeBase, kb_id)
    if kb:
        kb.doc_count = Document.query.filter_by(kb_id=kb_id).count()


def vectorize(doc):
    """
    对单个文档执行向量化，并更新文档状态
    :param doc: Document 对象
    :return: (是否成功, 提示信息)
    """
    kb = db.session.get(KnowledgeBase, doc.kb_id)
    if not kb:
        return False, "所属知识库不存在"
    try:
        doc.chunk_count = rag_service.ingest_document(
            kb.collection_name, doc.id, doc.file_name, doc.file_path, doc.file_type
        )
        doc.status = Document.STATUS_DONE
        doc.error_msg = None
        return True, f"向量化完成，共 {doc.chunk_count} 个片段"
    except Exception as e:
        doc.status = Document.STATUS_FAILED
        doc.error_msg = str(e)[:500]
        return False, f"向量化失败：{e}"
    finally:
        db.session.commit()


@doc_bp.get("")
@admin_required
def list_docs():
    """
    分页查询文档列表
    查询参数：page、size、kb_id、keyword
    """
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    kb_id = request.args.get("kb_id", type=int)
    keyword = request.args.get("keyword", "").strip()

    query = Document.query
    if kb_id:
        query = query.filter(Document.kb_id == kb_id)
    if keyword:
        query = query.filter(Document.file_name.like(f"%{keyword}%"))
    pagination = query.order_by(Document.id.desc()).paginate(page=page, per_page=size, error_out=False)
    return success(page_data(pagination))


@doc_bp.post("/upload")
@admin_required
def upload():
    """
    上传文档并立即向量化
    表单字段：kb_id（知识库ID）、file（文件）
    """
    kb_id = request.form.get("kb_id", type=int)
    file = request.files.get("file")
    if not kb_id or not db.session.get(KnowledgeBase, kb_id):
        return error("请选择有效的知识库")
    if not file or not file.filename:
        return error("请选择要上传的文件")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in Config.ALLOWED_EXTENSIONS:
        return error("仅支持 txt、md、pdf、docx 格式")

    # 中文文件名使用 uuid 重命名保存，原始文件名存数据库
    save_name = f"{uuid.uuid4().hex}.{ext}"
    abs_path = os.path.join(Config.UPLOAD_DIR, save_name)
    file.save(abs_path)

    doc = Document(
        kb_id=kb_id,
        file_name=file.filename,
        file_path=os.path.relpath(abs_path, BASE_DIR).replace("\\", "/"),
        file_type=ext,
        file_size=os.path.getsize(abs_path),
        upload_by=get_current_user().id,
    )
    db.session.add(doc)
    db.session.flush()
    refresh_doc_count(kb_id)
    db.session.commit()

    ok, msg = vectorize(doc)
    if not ok:
        return error(msg)
    return success(doc.to_dict(), msg)


@doc_bp.post("/<int:doc_id>/vectorize")
@admin_required
def re_vectorize(doc_id):
    """
    重新向量化指定文档（适用于待处理或失败的文档）
    :param doc_id: 文档ID
    """
    doc = db.session.get(Document, doc_id)
    if not doc:
        return error("文档不存在")
    ok, msg = vectorize(doc)
    return success(doc.to_dict(), msg) if ok else error(msg)


@doc_bp.delete("/<int:doc_id>")
@admin_required
def delete_doc(doc_id):
    """
    删除文档：删除向量片段、上传的原始文件以及数据库记录
    :param doc_id: 文档ID
    """
    doc = db.session.get(Document, doc_id)
    if not doc:
        return error("文档不存在")
    kb = db.session.get(KnowledgeBase, doc.kb_id)
    if kb:
        try:
            rag_service.delete_document_vectors(kb.collection_name, doc.id)
        except Exception:
            pass

    # 只删除 uploads 目录中的文件，示例文档保留
    abs_path = os.path.join(BASE_DIR, doc.file_path)
    if os.path.abspath(abs_path).startswith(os.path.abspath(Config.UPLOAD_DIR)) and os.path.exists(abs_path):
        os.remove(abs_path)

    kb_id = doc.kb_id
    db.session.delete(doc)
    db.session.flush()
    refresh_doc_count(kb_id)
    db.session.commit()
    return success(msg="删除成功")
