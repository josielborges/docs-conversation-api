from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from pgvector.sqlalchemy import Vector
import uuid


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    notebook_id = Column(BigInteger, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(BigInteger, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)  # Google embeddings are 768 dimensions
    filename = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notebook = relationship("Notebook", backref="embeddings")
    source = relationship("Source", backref="embeddings")
