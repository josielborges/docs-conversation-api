import tempfile
from typing import List
from pathlib import Path
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from markitdown import MarkItDown
from app.core import settings


def extract_text(file_content: bytes, filename: str) -> str:
    """Extract text from various file formats using MarkItDown."""
    md = MarkItDown()
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(file_content)
            tmp_file.flush()
        
        result = md.convert(tmp_path)
        return result.text_content
    except Exception as e:
        raise ValueError(f"Failed to extract text from {filename}: {str(e)}")
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]: 
    """Split text into semantic chunks using LangChain's SemanticChunker."""
    if not text or not text.strip():
        return []
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY
        )
        
        text_splitter = SemanticChunker(embeddings)
        chunks = text_splitter.split_text(text)
        
        return chunks
    except Exception as e:
        raise ValueError(f"Failed to chunk text: {str(e)}")
