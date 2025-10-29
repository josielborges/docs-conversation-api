from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.conversation import ConversationCreate
from app.schemas.chat_message import ChatRequest
from app.services import DatabaseService, vector_store, llm_service
from app.api.dependencies import verify_api_key
import uuid as uuid_pkg

router = APIRouter()


@router.post("/{notebook_id}/conversations")
async def create_conversation(
    notebook_id: str,
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    return await DatabaseService.create_conversation(db, notebook.id, conversation)


@router.get("/{notebook_id}/conversations")
async def get_conversations(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    return await DatabaseService.get_conversations(db, notebook.id)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(conversation_id)
    await DatabaseService.delete_conversation(db, public_id)
    return {"message": "Conversation deleted"}


@router.post("/conversations/{conversation_id}/chat")
async def chat(
    conversation_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(conversation_id)
    conversation = await DatabaseService.get_conversation(db, public_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await DatabaseService.add_chat_message(db, conversation.id, "user", request.message)
    
    count = await vector_store.get_collection_count(db, conversation.notebook_id)
    if count == 0:
        response_text = "Por favor, faça upload de documentos antes de fazer perguntas."
        await DatabaseService.add_chat_message(db, conversation.id, "assistant", response_text, [])
        return {"response": response_text, "sources": []}
    
    results = await vector_store.query(
        db,
        conversation.notebook_id,
        request.message,
        n_results=10,
        source_filter=request.enabled_sources if request.enabled_sources else None
    )
    
    context = "\n\n".join(results['documents'][0]) if results['documents'][0] else ""
    sources = list(set([meta['filename'] for meta in results['metadatas'][0]])) if results['metadatas'] else []
    
    response_text = llm_service.generate_chat_response(context, request.message)
    await DatabaseService.add_chat_message(db, conversation.id, "assistant", response_text, sources)
    
    return {"response": response_text, "sources": sources}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(conversation_id)
    conversation = await DatabaseService.get_conversation(db, public_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return await DatabaseService.get_chat_history(db, conversation.id)
