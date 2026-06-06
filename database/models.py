"""
MEOK AI Labs - Database Models
SQLAlchemy models with pgvector support
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Boolean,
    Integer,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False)
    name = Column(String(255))
    plan = Column(String(50), default="free")
    rate_limit = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="user")
    memories = relationship("Memory", back_populates="user")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content_hash = Column(String(64), nullable=False)
    framework = Column(String(50), nullable=False)
    content_type = Column(String(20), default="text")
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    violations = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")

    __table_args__ = (
        Index("idx_analysis_user_created", "user_id", "created_at"),
        Index("idx_analysis_framework", "framework"),
    )


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    content_embedding = Column(ARRAY(Float), nullable=False)
    memory_type = Column(String(50), default="episodic")
    tags = Column(ARRAY(String), default=list)
    importance = Column(Float, default=0.5)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index("idx_memory_user_type", "user_id", "memory_type"),
        Index("idx_memory_importance", "importance"),
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    capabilities = Column(ARRAY(String), default=list)
    status = Column(String(20), default="active")
    current_tasks = Column(Integer, default=0)
    max_concurrent = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="agent")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    instruction = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")
    status = Column(String(20), default="pending")
    result = Column(JSON)
    error = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    agent = relationship("Agent", back_populates="tasks")
    user = relationship("User")

    __table_args__ = (
        Index("idx_task_status", "status"),
        Index("idx_task_priority", "priority"),
        Index("idx_task_user_status", "user_id", "status"),
    )


class ConsciousnessState(Base):
    __tablename__ = "consciousness_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    state_type = Column(String(50))
    awareness_level = Column(Float, default=0.0)
    coherence = Column(Float, default=0.0)
    active_patterns = Column(JSON, default=list)
    anomalies = Column(JSON, default=list)
    metrics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_consciousness_session", "session_id", "created_at"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_user", "user_id", "created_at"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_created", "created_at"),
    )


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    url = Column(Text, nullable=False)
    events = Column(ARRAY(String), nullable=False)
    secret = Column(String(64))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)
    failure_count = Column(Integer, default=0)

    user = relationship("User")

    __table_args__ = (Index("idx_webhook_user", "user_id"),)
