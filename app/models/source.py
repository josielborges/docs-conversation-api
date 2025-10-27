from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    view_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notebook = relationship("Notebook", back_populates="sources")
