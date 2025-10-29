from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.models import DocumentEmbedding
from app.core import settings
import google.generativeai as genai
import uuid as uuid_pkg


class VectorStoreService:
    def __init__(self):
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google's API."""
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def _get_query_embedding(self, text: str) -> List[float]:
        """Generate embedding for query using Google's API."""
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    async def add_documents(self, db: AsyncSession, notebook_id: int, source_id: int, chunks: List[str], filename: str):
        """Add document chunks to the vector store."""
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk)
            doc_embedding = DocumentEmbedding(
                notebook_id=notebook_id,
                source_id=source_id,
                content=chunk,
                embedding=embedding,
                filename=filename,
                chunk_index=i
            )
            db.add(doc_embedding)
        await db.commit()
    
    async def query(self, db: AsyncSession, notebook_id: int, query_text: str, 
                   n_results: int = 10) -> dict:
        """Query the vector store using cosine similarity."""
        query_embedding = self._get_query_embedding(query_text)
        
        stmt = select(
            DocumentEmbedding.content,
            DocumentEmbedding.filename,
            DocumentEmbedding.embedding.cosine_distance(query_embedding).label('distance')
        ).where(
            DocumentEmbedding.notebook_id == notebook_id,
            DocumentEmbedding.enabled == True
        ).order_by('distance').limit(n_results)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        documents = [[row.content for row in rows]]
        metadatas = [[{"filename": row.filename} for row in rows]]
        
        return {"documents": documents, "metadatas": metadatas}
    
    async def delete_collection(self, db: AsyncSession, notebook_id: int):
        """Delete all embeddings for a notebook."""
        await db.execute(delete(DocumentEmbedding).where(DocumentEmbedding.notebook_id == notebook_id))
        await db.commit()
    
    async def get_collection_count(self, db: AsyncSession, notebook_id: int) -> int:
        """Get the number of embeddings for a notebook."""
        result = await db.execute(
            select(func.count(DocumentEmbedding.id)).where(DocumentEmbedding.notebook_id == notebook_id)
        )
        return result.scalar() or 0


vector_store = VectorStoreService()
