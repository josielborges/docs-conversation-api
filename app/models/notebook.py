from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sources = relationship("Source", back_populates="notebook", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="notebook", cascade="all, delete-orphan")
