from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas import (
    ConversationCreate, ConversationResponse,
    ChatRequest, ChatResponse, ChatMessageResponse
)
from app.services import DatabaseService, vector_store, llm_service
from app.api.dependencies import verify_api_key
from app.core import settings
import uuid as uuid_pkg

router = APIRouter()


@router.post("/notebooks/{public_id}/conversations", response_model=ConversationResponse)
async def create_conversation(
    public_id: uuid_pkg.UUID,
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new conversation in a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, public_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return await DatabaseService.create_conversation(db, db_notebook.id, conversation)


@router.get("/notebooks/{public_id}/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    public_id: uuid_pkg.UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all conversations for a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, public_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return await DatabaseService.get_conversations(db, db_notebook.id)


@router.delete("/{public_id}")
async def delete_conversation(
    public_id: uuid_pkg.UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a conversation."""
    await DatabaseService.delete_conversation(db, public_id)
    return {"message": "Conversation deleted"}


@router.post("/{public_id}/chat", response_model=ChatResponse)
async def chat(
    public_id: uuid_pkg.UUID,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Send a message in a conversation."""
    try:
        conversation = await DatabaseService.get_conversation(db, public_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        await DatabaseService.add_chat_message(db, conversation.id, "user", request.message)
        
        notebook_public_id = conversation.notebook.public_id
        count = vector_store.get_collection_count(notebook_public_id)
        
        if count == 0:
            response_text = "Por favor, faça upload de documentos antes de fazer perguntas."
            await DatabaseService.add_chat_message(db, conversation.id, "assistant", response_text, [])
            return ChatResponse(response=response_text, sources=[])
        
        n_results = min(settings.RAG_N_RESULTS, count)
        results = vector_store.query(
            notebook_public_id,
            request.message,
            n_results,
            request.enabled_sources if request.enabled_sources else None
        )
        
        context = "\n\n".join(results['documents'][0]) if results['documents'][0] else ""
        sources = list(set([meta['filename'] for meta in results['metadatas'][0]])) if results['metadatas'] else []
        
        response_text = llm_service.generate_response(context, request.message)
        await DatabaseService.add_chat_message(db, conversation.id, "assistant", response_text, sources)
        
        return ChatResponse(response=response_text, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{public_id}/messages", response_model=List[ChatMessageResponse])
async def get_conversation_messages(
    public_id: uuid_pkg.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a conversation."""
    conversation = await DatabaseService.get_conversation(db, public_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await DatabaseService.get_chat_history(db, conversation.id)
