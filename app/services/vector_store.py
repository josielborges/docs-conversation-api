import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Dict, List, Optional
import uuid


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.collections: Dict[str, any] = {}
    
    def get_or_create_collection(self, notebook_id: str):
        """Get or create a ChromaDB collection for a notebook."""
        if notebook_id not in self.collections:
            self.collections[notebook_id] = self.client.get_or_create_collection(
                name=f"notebook_{notebook_id}",
                embedding_function=embedding_functions.DefaultEmbeddingFunction()
            )
        return self.collections[notebook_id]
    
    def add_documents(self, notebook_id: str, chunks: List[str], filename: str):
        """Add document chunks to the vector store."""
        collection = self.get_or_create_collection(notebook_id)
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{"filename": filename, "chunk": i}],
                ids=[f"{filename}_{i}_{uuid.uuid4()}"]
            )
    
    def query(self, notebook_id: str, query_text: str, n_results: int = 10, 
              source_filter: Optional[List[str]] = None) -> dict:
        """Query the vector store."""
        collection = self.get_or_create_collection(notebook_id)
        count = collection.count()
        
        if count == 0:
            return {"documents": [[]], "metadatas": [[]]}
        
        n_results = min(n_results, count)
        
        if source_filter:
            return collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"filename": {"$in": source_filter}}
            )
        else:
            return collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
    
    def delete_collection(self, notebook_id: str):
        """Delete a collection."""
        self.client.delete_collection(f"notebook_{notebook_id}")
        if notebook_id in self.collections:
            del self.collections[notebook_id]
    
    def get_collection_count(self, notebook_id: str) -> int:
        """Get the number of documents in a collection."""
        collection = self.get_or_create_collection(notebook_id)
        return collection.count()


vector_store = VectorStoreService()
