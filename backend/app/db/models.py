from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    TIMESTAMP,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True)
    name = Column(String(100))
    preferred_language = Column(String(5), default="sw")
    county = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    crop = Column(String(50), nullable=False)
    location_lat = Column(Float)
    location_lon = Column(Float)
    county = Column(String(50))
    size_acres = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="farms")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="SET NULL"))
    language = Column(String(5))
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role = Column(String(10), nullable=False)
    content = Column(Text)
    language = Column(String(5))
    image_url = Column(Text)
    agent_trace = Column(JSON)
    sources = Column(JSON)
    latency_ms = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    tool_calls = relationship(
        "ToolCall", back_populates="message", cascade="all, delete-orphan"
    )


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(200), nullable=False)
    language = Column(String(5), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_text_en = Column(Text)
    metadata_json = Column("metadata", JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String(100), nullable=False)
    name_sw = Column(String(100), nullable=False)
    crop = Column(String(50), nullable=False)
    symptoms = Column(Text)
    treatment_en = Column(Text)
    treatment_sw = Column(Text)
    sources = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE")
    )
    tool_name = Column(String(50), nullable=False)
    arguments = Column(JSON)
    result = Column(JSON)
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    message = relationship("Message", back_populates="tool_calls")
