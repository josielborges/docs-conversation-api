from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.models import Notebook, Conversation, ChatMessage, Source, ApiKey
from app.schemas import (
    NotebookCreate, NotebookResponse,
    ConversationCreate, ConversationResponse,
    ChatMessageResponse, SourceResponse,
    ApiKeyCreate, ApiKeyResponse
)
import uuid as uuid_pkg
import secrets


class DatabaseService:
    @staticmethod
    async def create_notebook(db: AsyncSession, notebook: NotebookCreate) -> NotebookResponse:
        db_notebook = Notebook(name=notebook.name)
        db.add(db_notebook)
        await db.commit()
        await db.refresh(db_notebook)
        return NotebookResponse.model_validate(db_notebook)
    
    @staticmethod
    async def get_all_notebooks(db: AsyncSession) -> List[NotebookResponse]:
        result = await db.execute(select(Notebook))
        notebooks = result.scalars().all()
        return [NotebookResponse.model_validate(nb) for nb in notebooks]
    
    @staticmethod
    async def get_notebook(db: AsyncSession, public_id: uuid_pkg.UUID) -> Optional[Notebook]:
        result = await db.execute(select(Notebook).where(Notebook.public_id == public_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_notebook(db: AsyncSession, public_id: uuid_pkg.UUID, name: str) -> NotebookResponse:
        result = await db.execute(select(Notebook).where(Notebook.public_id == public_id))
        notebook = result.scalar_one_or_none()
        if notebook:
            notebook.name = name
            await db.commit()
            await db.refresh(notebook)
        return NotebookResponse.model_validate(notebook)
    
    @staticmethod
    async def update_notebook_summary(db: AsyncSession, public_id: uuid_pkg.UUID, summary: str):
        result = await db.execute(select(Notebook).where(Notebook.public_id == public_id))
        notebook = result.scalar_one_or_none()
        if notebook:
            notebook.summary = summary
            await db.commit()
    
    @staticmethod
    async def delete_notebook(db: AsyncSession, public_id: uuid_pkg.UUID):
        await db.execute(delete(Notebook).where(Notebook.public_id == public_id))
        await db.commit()
    
    @staticmethod
    async def create_conversation(db: AsyncSession, notebook_id: int, 
                                  conversation: ConversationCreate) -> ConversationResponse:
        db_conversation = Conversation(
            notebook_id=notebook_id,
            title=conversation.title
        )
        db.add(db_conversation)
        await db.commit()
        await db.refresh(db_conversation)
        return ConversationResponse.model_validate(db_conversation)
    
    @staticmethod
    async def get_conversations(db: AsyncSession, notebook_id: int) -> List[ConversationResponse]:
        result = await db.execute(
            select(Conversation).where(Conversation.notebook_id == notebook_id)
        )
        conversations = result.scalars().all()
        return [ConversationResponse.model_validate(conv) for conv in conversations]
    
    @staticmethod
    async def get_conversation(db: AsyncSession, public_id: uuid_pkg.UUID) -> Optional[Conversation]:
        result = await db.execute(select(Conversation).where(Conversation.public_id == public_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_conversation(db: AsyncSession, public_id: uuid_pkg.UUID):
        await db.execute(delete(Conversation).where(Conversation.public_id == public_id))
        await db.commit()
    
    @staticmethod
    async def add_chat_message(db: AsyncSession, conversation_id: int, role: str, 
                               content: str, sources: List[str] = None) -> ChatMessageResponse:
        db_message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources or []
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return ChatMessageResponse.model_validate(db_message)
    
    @staticmethod
    async def get_chat_history(db: AsyncSession, conversation_id: int) -> List[ChatMessageResponse]:
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        )
        messages = result.scalars().all()
        return [ChatMessageResponse.model_validate(msg) for msg in messages]
    
    @staticmethod
    async def add_source(db: AsyncSession, notebook_id: int, name: str, 
                        source_type: str, url: Optional[str] = None) -> Source:
        db_source = Source(
            notebook_id=notebook_id,
            name=name,
            type=source_type,
            view_url=url
        )
        db.add(db_source)
        await db.commit()
        await db.refresh(db_source)
        return db_source
    
    @staticmethod
    async def get_sources(db: AsyncSession, notebook_id: int) -> List[SourceResponse]:
        result = await db.execute(select(Source).where(Source.notebook_id == notebook_id))
        sources = result.scalars().all()
        return [SourceResponse.model_validate(src) for src in sources]
    
    @staticmethod
    async def delete_source(db: AsyncSession, public_id: uuid_pkg.UUID):
        await db.execute(delete(Source).where(Source.public_id == public_id))
        await db.commit()
    
    @staticmethod
    async def create_api_key(db: AsyncSession, api_key_create: ApiKeyCreate) -> tuple[ApiKeyResponse, str]:
        api_key = f"dca_{secrets.token_urlsafe(32)}"
        db_api_key = ApiKey(key=api_key, name=api_key_create.name)
        db.add(db_api_key)
        await db.commit()
        await db.refresh(db_api_key)
        return ApiKeyResponse.model_validate(db_api_key), api_key
    
    @staticmethod
    async def get_all_api_keys(db: AsyncSession) -> List[ApiKeyResponse]:
        result = await db.execute(select(ApiKey))
        api_keys = result.scalars().all()
        return [ApiKeyResponse.model_validate(key) for key in api_keys]
    
    @staticmethod
    async def validate_api_key(db: AsyncSession, api_key: str) -> bool:
        result = await db.execute(select(ApiKey).where(ApiKey.key == api_key, ApiKey.is_active == True))
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def delete_api_key(db: AsyncSession, public_id: uuid_pkg.UUID):
        await db.execute(delete(ApiKey).where(ApiKey.public_id == public_id))
        await db.commit()
