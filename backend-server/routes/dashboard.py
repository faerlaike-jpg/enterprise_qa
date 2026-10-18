"""
管理员首页数据统计接口
"""
from datetime import date, timedelta

from flask import Blueprint
from sqlalchemy import func

from extensions import db
from models.chat import ChatMessage, ChatSession, Feedback
from models.document import Document
from models.knowledge_base import KnowledgeBase
from models.user import User
from utils.auth import admin_required
from utils.response import success

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/stats")
@admin_required
def stats():
    """
    首页统计数据
    返回：
      cards       -> 顶部统计卡片
      trend       -> 近 7 天问答趋势
      kb_dist     -> 各知识库文档分布
      user_rank   -> 用户提问排行 Top5
      doc_status  -> 文档处理状态分布
      satisfaction-> 回答满意度
    """
    today = date.today()

    # ---------- 统计卡片 ----------
    cards = {
        "user_count": User.query.count(),
        "kb_count": KnowledgeBase.query.count(),
        "doc_count": Document.query.count(),
        "chunk_count": int(db.session.query(func.coalesce(func.sum(Document.chunk_count), 0)).scalar()),
        "question_total": ChatMessage.query.filter_by(role="user").count(),
        "today_question": ChatMessage.query.filter(
            ChatMessage.role == "user", func.date(ChatMessage.create_time) == today
        ).count(),
    }

    # ---------- 近 7 天问答趋势 ----------
    start = today - timedelta(days=6)
    rows = (
        db.session.query(func.date(ChatMessage.create_time), func.count(ChatMessage.id))
        .filter(ChatMessage.role == "user", func.date(ChatMessage.create_time) >= start)
        .group_by(func.date(ChatMessage.create_time))
        .all()
    )
    count_map = {str(d): c for d, c in rows}
    days = [start + timedelta(days=i) for i in range(7)]
    trend = {
        "dates": [d.strftime("%m-%d") for d in days],
        "counts": [count_map.get(str(d), 0) for d in days],
    }

    # ---------- 知识库文档分布 ----------
    kb_dist = [{"name": kb.name, "value": kb.doc_count} for kb in KnowledgeBase.query.all()]

    # ---------- 用户提问排行 ----------
    rank_rows = (
        db.session.query(User.nickname, func.count(ChatMessage.id).label("cnt"))
        .join(ChatSession, ChatSession.user_id == User.id)
        .join(ChatMessage, ChatMessage.session_id == ChatSession.id)
        .filter(ChatMessage.role == "user")
        .group_by(User.id, User.nickname)
        .order_by(func.count(ChatMessage.id).desc())
        .limit(5)
        .all()
    )
    user_rank = [{"name": n, "value": c} for n, c in rank_rows]

    # ---------- 文档状态分布 ----------
    status_names = {0: "待处理", 1: "已完成", 2: "失败"}
    status_rows = db.session.query(Document.status, func.count(Document.id)).group_by(Document.status).all()
    doc_status = [{"name": status_names.get(s, str(s)), "value": c} for s, c in status_rows]

    # ---------- 满意度 ----------
    like = Feedback.query.filter_by(type=1).count()
    dislike = Feedback.query.filter_by(type=-1).count()
    satisfaction = {
        "like": like,
        "dislike": dislike,
        "rate": round(like * 100 / (like + dislike), 1) if like + dislike else 100.0,
    }

    return success(
        {
            "cards": cards,
            "trend": trend,
            "kb_dist": kb_dist,
            "user_rank": user_rank,
            "doc_status": doc_status,
            "satisfaction": satisfaction,
        }
    )
