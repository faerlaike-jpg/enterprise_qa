"""
智能问答接口：会话管理、SSE 流式问答、消息反馈、问答记录审计
"""
import json

from flask import Blueprint, Response, request, stream_with_context

from extensions import db
from models.chat import ChatMessage, ChatSession, Feedback
from models.knowledge_base import KnowledgeBase
from models.user import User
from services.agent_service import stream_chat
from utils.auth import admin_required, get_current_user, login_required
from utils.response import error, success

chat_bp = Blueprint("chat", __name__)

# 携带给大模型的历史消息条数（一问一答算 2 条）
HISTORY_LIMIT = 6


def get_own_session(session_id):
    """
    获取属于当前用户的会话，防止越权访问他人会话
    :param session_id: 会话ID
    :return: ChatSession 或 None
    """
    session = db.session.get(ChatSession, session_id)
    if not session or session.user_id != get_current_user().id:
        return None
    return session


def sse(data):
    """
    将字典封装为 SSE 数据帧
    :param data: 事件字典
    :return: 'data: {...}\\n\\n' 格式字符串
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ----------------------------------------------------------------------
# 会话管理
# ----------------------------------------------------------------------
@chat_bp.get("/sessions")
@login_required
def list_sessions():
    """查询当前用户的会话列表，按更新时间倒序"""
    sessions = (
        ChatSession.query.filter_by(user_id=get_current_user().id)
        .order_by(ChatSession.update_time.desc(), ChatSession.id.desc())
        .all()
    )
    return success([s.to_dict() for s in sessions])


@chat_bp.post("/sessions")
@login_required
def create_session():
    """
    新建会话
    请求体：{"kb_id": 1}
    """
    body = request.get_json(silent=True) or {}
    session = ChatSession(user_id=get_current_user().id, kb_id=body.get("kb_id"), title="新对话")
    db.session.add(session)
    db.session.commit()
    return success(session.to_dict())


@chat_bp.put("/sessions/<int:session_id>")
@login_required
def update_session(session_id):
    """
    修改会话标题或切换知识库
    :param session_id: 会话ID
    """
    session = get_own_session(session_id)
    if not session:
        return error("会话不存在")
    body = request.get_json(silent=True) or {}
    if body.get("title"):
        session.title = body["title"][:200]
    if "kb_id" in body:
        session.kb_id = body["kb_id"]
    db.session.commit()
    return success(session.to_dict())


@chat_bp.delete("/sessions/<int:session_id>")
@login_required
def delete_session(session_id):
    """
    删除会话及其全部消息
    :param session_id: 会话ID
    """
    session = get_own_session(session_id)
    if not session:
        return error("会话不存在")
    ChatMessage.query.filter_by(session_id=session_id).delete()
    db.session.delete(session)
    db.session.commit()
    return success(msg="删除成功")


@chat_bp.get("/sessions/<int:session_id>/messages")
@login_required
def list_messages(session_id):
    """
    查询会话中的全部消息
    :param session_id: 会话ID
    """
    session = get_own_session(session_id)
    if not session:
        return error("会话不存在")
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.id.asc()).all()
    return success([m.to_dict() for m in messages])


# ----------------------------------------------------------------------
# 流式问答
# ----------------------------------------------------------------------
@chat_bp.post("/stream")
@login_required
def chat_stream():
    """
    SSE 流式问答
    请求体：{"session_id": 1, "question": "年假有几天？"}
    事件类型：
      tool      -> Agent 正在调用工具
      tool_done -> 工具调用完成
      token     -> 回答的增量文本
      done      -> 回答结束，携带引用来源与消息ID
      error     -> 出错
    """
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    session = get_own_session(body.get("session_id"))
    if not session:
        return error("会话不存在")
    if not question:
        return error("问题不能为空")
    kb = db.session.get(KnowledgeBase, session.kb_id) if session.kb_id else None
    if not kb:
        return error("请先选择知识库")

    # 读取最近的历史消息作为上下文
    recent = (
        ChatMessage.query.filter_by(session_id=session.id)
        .order_by(ChatMessage.id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in reversed(recent)]

    # 保存用户提问；首次提问时用问题作为会话标题
    db.session.add(ChatMessage(session_id=session.id, role="user", content=question))
    if session.title == "新对话":
        session.title = question[:30]
    db.session.commit()

    collection_name = kb.collection_name
    session_id = session.id

    def generate():
        """SSE 事件生成器：逐步推送大模型输出，结束后保存回答"""
        sources = []
        answer = ""
        try:
            for event in stream_chat(collection_name, question, history, sources):
                if event["type"] == "token":
                    answer += event["content"]
                yield sse(event)
        except Exception as e:
            yield sse({"type": "error", "content": f"大模型调用失败：{e}"})

        if answer:
            msg = ChatMessage(session_id=session_id, role="assistant", content=answer, sources=sources)
            db.session.add(msg)
            db.session.query(ChatSession).filter_by(id=session_id).update({"update_time": db.func.now()})
            db.session.commit()
            yield sse({"type": "done", "message_id": msg.id, "sources": sources})
        else:
            yield sse({"type": "done", "message_id": None, "sources": []})

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return Response(stream_with_context(generate()), mimetype="text/event-stream", headers=headers)


# ----------------------------------------------------------------------
# 反馈
# ----------------------------------------------------------------------
@chat_bp.post("/messages/<int:message_id>/feedback")
@login_required
def feedback(message_id):
    """
    对 AI 回答点赞 / 点踩，再次提交同类型则取消
    请求体：{"type": 1 或 -1}
    """
    fb_type = (request.get_json(silent=True) or {}).get("type")
    if fb_type not in (1, -1):
        return error("参数错误")
    user_id = get_current_user().id
    record = Feedback.query.filter_by(message_id=message_id, user_id=user_id).first()
    if record and record.type == fb_type:
        db.session.delete(record)
        fb_type = 0
    elif record:
        record.type = fb_type
    else:
        db.session.add(Feedback(message_id=message_id, user_id=user_id, type=fb_type))
    db.session.commit()
    return success({"type": fb_type})


# ----------------------------------------------------------------------
# 问答记录（管理员审计）
# ----------------------------------------------------------------------
@chat_bp.get("/records")
@admin_required
def records():
    """
    分页查询全部用户的问答记录（问题 + 对应回答）
    查询参数：page、size、keyword、kb_id
    """
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "").strip()
    kb_id = request.args.get("kb_id", type=int)

    query = (
        db.session.query(ChatMessage, ChatSession, User)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .join(User, ChatSession.user_id == User.id)
        .filter(ChatMessage.role == "user")
    )
    if keyword:
        query = query.filter(ChatMessage.content.like(f"%{keyword}%"))
    if kb_id:
        query = query.filter(ChatSession.kb_id == kb_id)

    total = query.count()
    rows = query.order_by(ChatMessage.id.desc()).offset((page - 1) * size).limit(size).all()
    kb_names = {kb.id: kb.name for kb in KnowledgeBase.query.all()}

    result = []
    for q, s, u in rows:
        # 查找紧随该问题之后的回答
        answer = (
            ChatMessage.query.filter(
                ChatMessage.session_id == q.session_id, ChatMessage.id > q.id, ChatMessage.role == "assistant"
            )
            .order_by(ChatMessage.id.asc())
            .first()
        )
        result.append(
            {
                "id": q.id,
                "question": q.content,
                "answer": answer.content if answer else "",
                "sources": answer.sources if answer and answer.sources else [],
                "username": u.username,
                "nickname": u.nickname,
                "kb_name": kb_names.get(s.kb_id, "-"),
                "create_time": q.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return success({"list": result, "total": total, "page": page, "size": size})
