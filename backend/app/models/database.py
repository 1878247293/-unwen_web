"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # admin, user
    status = Column(String(20), default="pending", nullable=False)  # pending, active, disabled
    department = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    papers = relationship("Paper", back_populates="creator", foreign_keys="Paper.created_by")
    notes = relationship("Note", back_populates="creator", foreign_keys="Note.created_by")
    tags = relationship("Tag", back_populates="creator", foreign_keys="Tag.created_by")
    ai_conversations = relationship("AIConversation", back_populates="user")


class Paper(Base):
    """论文表"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(Text, nullable=True)
    journal = Column(String(200), nullable=True)
    year = Column(Integer, nullable=True, index=True)
    volume = Column(String(50), nullable=True)  # 卷号
    issue = Column(String(50), nullable=True)   # 期号
    pages = Column(String(50), nullable=True)   # 页码
    doi = Column(String(100), nullable=True, unique=True)
    arxiv_id = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)    # 论文链接
    pdf_path = Column(String(500), nullable=True)
    abstract = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    notes_preview = Column(Text, nullable=True)  # 笔记预览
    reading_status = Column(String(20), default="unread", nullable=False, index=True)  # unread, reading, read
    reading_progress = Column(Integer, default=0, nullable=False)  # 阅读进度 0-100
    is_shared = Column(Boolean, default=False, nullable=False, index=True)  # 是否共享：False=私人论文，True=共享论文
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    creator = relationship("User", back_populates="papers", foreign_keys=[created_by])
    notes = relationship("Note", back_populates="paper", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="paper_tags", back_populates="papers")
    reading_history = relationship("ReadingHistory", back_populates="paper", cascade="all, delete-orphan")


class Note(Base):
    """笔记表"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general", nullable=False)  # general, summary, method, conclusion, etc.
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    paper = relationship("Paper", back_populates="notes")
    creator = relationship("User", back_populates="notes", foreign_keys=[created_by])


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True)
    color = Column(String(20), default="#1890ff", nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    creator = relationship("User", back_populates="tags", foreign_keys=[created_by])
    papers = relationship("Paper", secondary="paper_tags", back_populates="tags")


class PaperTag(Base):
    """论文-标签关联表"""
    __tablename__ = "paper_tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AIConversation(Base):
    """AI对话会话表"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    context_type = Column(String(50), nullable=True)  # paper, project, etc.
    context_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")


class AIMessage(Base):
    """AI对话消息表"""
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    conversation = relationship("AIConversation", back_populates="messages")


class UserAIQuota(Base):
    """用户AI额度表"""
    __tablename__ = "user_ai_quotas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    daily_limit = Column(Integer, default=50, nullable=False)
    monthly_limit = Column(Integer, default=1000, nullable=False)
    daily_used = Column(Integer, default=0, nullable=False)
    monthly_used = Column(Integer, default=0, nullable=False)
    reset_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AuditLog(Base):
    """操作日志表"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, login, etc.
    table_name = Column(String(50), nullable=True)
    record_id = Column(Integer, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ReadingHistory(Base):
    """阅读历史记录表"""
    __tablename__ = "reading_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)  # 开始阅读时间
    end_time = Column(DateTime, nullable=True)  # 结束阅读时间
    duration_seconds = Column(Integer, default=0, nullable=False)  # 阅读时长（秒）
    progress_before = Column(Integer, default=0, nullable=False)  # 阅读前进度
    progress_after = Column(Integer, default=0, nullable=False)  # 阅读后进度
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    paper = relationship("Paper", back_populates="reading_history")


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, index=True)  # 父评论ID，用于回复功能
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    paper = relationship("Paper", backref="comments")
    user = relationship("User", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies", foreign_keys=[parent_id])


class Discussion(Base):
    """讨论表 - 交流广场公共讨论区"""
    __tablename__ = "discussions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False, index=True)
    is_hidden = Column(Boolean, default=False, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("discussions.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, index=True)

    # 关系
    user = relationship("User", backref="discussions", foreign_keys=[user_id])
    parent = relationship("Discussion", remote_side=[id], backref="replies", foreign_keys=[parent_id])


class SystemSettings(Base):
    """系统设置表 - 存储全局配置"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DiscussionLike(Base):
    """讨论点赞表"""
    __tablename__ = "discussion_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    discussion = relationship("Discussion", backref="likes")
    user = relationship("User", backref="discussion_likes")


class DiscussionFavorite(Base):
    """讨论收藏表"""
    __tablename__ = "discussion_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    discussion = relationship("Discussion", backref="favorites")
    user = relationship("User", backref="discussion_favorites")


class DiscussionReport(Base):
    """讨论举报表"""
    __tablename__ = "discussion_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, handled, rejected
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    handled_at = Column(DateTime, nullable=True)
    handled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # 关系
    discussion = relationship("Discussion", backref="reports")
    reporter = relationship("User", backref="filed_reports", foreign_keys=[user_id])
    handler = relationship("User", backref="handled_reports", foreign_keys=[handled_by])

