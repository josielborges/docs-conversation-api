from sqlalchemy import Column, String, Text, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sources = relationship("Source", back_populates="notebook", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="notebook", cascade="all, delete-orphan")
