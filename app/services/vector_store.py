import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Dict, List, Optional
import uuid as uuid_pkg


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.collections: Dict[str, any] = {}
    
    def get_or_create_collection(self, notebook_public_id: uuid_pkg.UUID):
        """Get or create a ChromaDB collection for a notebook."""
        key = str(notebook_public_id)
        if key not in self.collections:
            self.collections[key] = self.client.get_or_create_collection(
                name=f"notebook_{key}",
                embedding_function=embedding_functions.DefaultEmbeddingFunction()
            )
        return self.collections[key]
    
    def add_documents(self, notebook_public_id: uuid_pkg.UUID, chunks: List[str], filename: str):
        """Add document chunks to the vector store."""
        collection = self.get_or_create_collection(notebook_public_id)
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{"filename": filename, "chunk": i}],
                ids=[f"{filename}_{i}_{uuid_pkg.uuid4()}"]
            )
    
    def query(self, notebook_public_id: uuid_pkg.UUID, query_text: str, n_results: int = 10, 
              source_filter: Optional[List[str]] = None) -> dict:
        """Query the vector store."""
        collection = self.get_or_create_collection(notebook_public_id)
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
    
    def delete_collection(self, notebook_public_id: uuid_pkg.UUID):
        """Delete a collection."""
        key = str(notebook_public_id)
        self.client.delete_collection(f"notebook_{key}")
        if key in self.collections:
            del self.collections[key]
    
    def get_collection_count(self, notebook_public_id: uuid_pkg.UUID) -> int:
        """Get the number of documents in a collection."""
        collection = self.get_or_create_collection(notebook_public_id)
        return collection.count()


vector_store = VectorStoreService()
