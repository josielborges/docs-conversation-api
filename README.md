# Docs Conversation API

A powerful RAG (Retrieval-Augmented Generation) based API for building conversational interfaces that can interact with documents. Built with FastAPI, PostgreSQL, ChromaDB, and Google Gemini.

## Features

- 📚 **Notebook Management**: Organize documents into notebooks
- 💬 **Conversational AI**: Chat with your documents using natural language
- 📄 **Multiple Document Formats**: Support for PDF, DOCX, TXT files
- 🔗 **Web Scraping**: Add content from URLs
- 📖 **Estante Integration**: Import books from SENAI's Estante platform
- 🔑 **API Key Authentication**: Secure API access
- 📊 **Document Summarization**: Generate summaries of your document collections
- 🎯 **Source Filtering**: Query specific documents in your notebook

## Architecture

- **FastAPI**: Modern async web framework
- **PostgreSQL with pgvector**: Database for metadata and vector embeddings
- **Google Gemini**: LLM for text generation
- **SQLAlchemy**: Async ORM
- **Alembic**: Database migrations

## Project Structure

```
app/
├── api/
│   ├── v1/
│   │   ├── notebooks.py      # Notebook endpoints
│   │   ├── conversations.py  # Chat endpoints
│   │   ├── links.py          # Web link endpoints
│   │   ├── api_keys.py       # API key management
│   │   └── estante.py        # Estante integration
│   └── dependencies.py       # Shared dependencies
├── core/
│   └── config.py             # Configuration
├── db/
│   └── base.py               # Database setup
├── models/                   # SQLAlchemy models
├── schemas/                  # Pydantic schemas
├── services/
│   ├── vector_store.py       # ChromaDB service
│   ├── llm_service.py        # Gemini service
│   └── database_service.py   # Database operations
├── utils/
│   ├── text_extraction.py    # Document processing
│   └── web_scraper.py        # Web scraping
└── main.py                   # FastAPI app
```

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd docs-conversation-api
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
GEMINI_API_KEY=your_gemini_api_key
ESTANTE_USERNAME=your_estante_username
ESTANTE_PASSWORD=your_estante_password
```

4. Run database migrations:
```bash
uv run alembic upgrade head
```

5. Start the server:
```bash
./scripts/start.sh
# or
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Create a Notebook
```bash
curl -X POST http://localhost:8000/notebooks \
  -H "Content-Type: application/json" \
  -d '{"name": "My Research"}'
```

### Upload Documents
```bash
curl -X POST http://localhost:8000/notebooks/{notebook_id}/upload \
  -F "files=@document.pdf"
```

### Create a Conversation
```bash
curl -X POST http://localhost:8000/notebooks/{notebook_id}/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Research Questions"}'
```

### Chat with Documents
```bash
curl -X POST http://localhost:8000/conversations/{conversation_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics?", "enabled_sources": []}'
```

## Development

### Run with auto-reload:
```bash
uv run uvicorn app.main:app --reload
```

### Create a new migration:
```bash
uv run alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
uv run alembic upgrade head
```

## License

MIT