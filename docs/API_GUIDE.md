# API Guide

## Authentication

- **Master Key**: API key management endpoints require a master key via `X-Master-Key` header
- **API Key**: All other endpoints (except health check) require an API key via `X-API-Key` header

## Endpoints

### Health Check

```http
GET /health
```

Returns API health status.

### API Keys

#### Create API Key
```http
POST /api-keys
Content-Type: application/json
X-Master-Key: your_master_key

{
  "name": "My API Key"
}
```

#### List API Keys
```http
GET /api-keys
X-Master-Key: your_master_key
```

#### Delete API Key
```http
DELETE /api-keys/{key_id}
X-Master-Key: your_master_key
```

### Notebooks

#### Create Notebook
```http
POST /notebooks
Content-Type: application/json
X-API-Key: your_api_key

{
  "name": "My Notebook"
}
```

#### List Notebooks
```http
GET /notebooks
X-API-Key: your_api_key
```

#### Rename Notebook
```http
PUT /notebooks/{notebook_id}
Content-Type: application/json
X-API-Key: your_api_key

{
  "name": "New Name"
}
```

#### Delete Notebook
```http
DELETE /notebooks/{notebook_id}
X-API-Key: your_api_key
```

#### Upload Files
```http
POST /notebooks/{notebook_id}/upload
Content-Type: multipart/form-data
X-API-Key: your_api_key

files: [file1.pdf, file2.docx]
```

#### Add Web Link
```http
POST /notebooks/{notebook_id}/add-link
Content-Type: application/json
X-API-Key: your_api_key

{
  "url": "https://example.com/article"
}
```

#### Get Sources
```http
GET /notebooks/{notebook_id}/sources
```

#### Get Summary
```http
GET /notebooks/{notebook_id}/summary
```

#### Generate Summary
```http
POST /notebooks/{notebook_id}/generate-summary
```

### Conversations

#### Create Conversation
```http
POST /notebooks/{notebook_id}/conversations
Content-Type: application/json
X-API-Key: your_api_key

{
  "title": "Research Questions"
}
```

#### List Conversations
```http
GET /notebooks/{notebook_id}/conversations
X-API-Key: your_api_key
```

#### Delete Conversation
```http
DELETE /conversations/{conversation_id}
X-API-Key: your_api_key
```

#### Chat
```http
POST /conversations/{conversation_id}/chat
Content-Type: application/json
X-API-Key: your_api_key

{
  "message": "What are the main topics?",
  "enabled_sources": ["document1.pdf", "document2.pdf"]
}
```

#### Get Messages
```http
GET /conversations/{conversation_id}/messages
```

### Estante Integration

#### Get Areas
```http
GET /estante/areas
```

#### Get Modalities
```http
GET /estante/areas/{area_id}/modalidades
```

#### Get Books
```http
GET /estante/areas/{area_id}/modalidades/{modalidade_id}/livros
```

#### Add Books to Notebook
```http
POST /estante/notebooks/{notebook_id}/add-livros
Content-Type: application/json
X-API-Key: your_api_key

{
  "livros": [
    {
      "nome": "Book Name",
      "driveId": "drive_id",
      "webViewLink": "https://..."
    }
  ]
}
```

## Response Formats

### Success Response
```json
{
  "id": "uuid",
  "name": "Resource Name",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production use.

## Best Practices

1. Always store API keys securely
2. Use source filtering in chat requests for better performance
3. Generate summaries after adding multiple documents
4. Delete unused notebooks to free up resources
5. Use meaningful names for notebooks and conversations
