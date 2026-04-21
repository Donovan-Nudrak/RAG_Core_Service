# RAG Core Service

## Introduction

RAG Core Service is a lightweight Retrieval-Augmented Generation (RAG) API built with FastAPI.  
It combines semantic retrieval with large language models to provide context-aware answers based on both static and dynamic data sources.

The system is designed to be modular, extensible, and suitable for experimentation or integration into larger applications.

---

## Tech Stack

- **Backend Framework**: FastAPI
- **Language**: Python 3.10+
- **Database**: SQLite (SQLAlchemy ORM)
- **LLM Provider**: OpenRouter API
- **Embeddings**: External embedding model via API
- **HTTP Client**: Requests
- **Testing**: Bash + curl
- **Data Handling**: Pydantic

---

## Architecture Overview

The project follows a layered architecture with clear separation of concerns:

- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Implements RAG orchestration logic
- **Domain Layer**: Defines core entities and interfaces
- **Infrastructure Layer**: Handles persistence, embeddings, and retrieval

Dependency injection is used to decouple components and improve testability.

---
## Project Structure

```
RAG_Core_Service/  
├── api
│   ├── json_response.py
│   ├── routes.py
│   └── schemas.py
|
├── core
│   ├── config.py
│   ├── container.py
│   └── dependencies.py
|
├── data
│   ├── computing_timeline.json
│   └── IA_concepts.txt
|
├── domain
│   ├── interfaces.py
│   └── models.py
|
├── infrastructure
│   ├── data_loader.py
│   ├── LLM
│   │   ├── embedding_client.py
│   │   └── llm_client.py
|   |
│   ├── persistence
│   │   ├── models.py
│   │   └── sqlite_migrate.py
|   |
│   ├── retriever.py
│   └── vector_store.py
|
├── main.py
|
├── requirements.txt
|
├── scripts
|   └── full_test.sh
|
├── services
│   ├── llm_service.py
│   └── rag_service.py
|
└── utils
    └── text_normalize.py

```

---

## API Endpoints

### Ask a question

Request:

```bash
curl -X POST http://127.0.0.1:8000/ask \
-H "Content-Type: application/json" \
-d '{"question": "What is artificial intelligence?"}'
```

Response: 

```json
{
  "answer": "..."
}
```

---
### Document management

- `POST /documents` → Create document
- `GET /documents` → List documents
- `GET /documents/{id}` → Retrieve document
- `PUT /documents/{id}` → Update document
- `DELETE /documents/{id}` → Soft delete document
### Reindex documents

```
POST /documents/reindex
```

Rebuilds the vector index using both file-based and database documents.

---
## Design Decisions

- **Layered Architecture**  
    Enforces separation of concerns and improves maintainability.
- **Protocol-based Interfaces (Domain Layer)**  
    Enables flexible substitution of retrievers and generators.
- **Hybrid Data Source**  
    Combines static files and database content for retrieval.
- **In-memory Vector Store**  
    Simplifies implementation and avoids external dependencies.
- **Soft Delete Strategy**  
    Preserves data integrity while allowing logical deletion.
- **Normalization Pipeline**  
    Ensures clean, readable LLM outputs.
- **Externalized LLM and Embeddings**  
    Keeps the system provider-agnostic and easily configurable.

---
## Features

- Retrieval-Augmented Generation (RAG) pipeline
- Semantic search using embeddings
- Hybrid document ingestion (files + database)
- Automatic document chunking and deduplication
- Context-aware answer generation
- Text normalization and cleanup
- Reindexing support
- Automated API testing via script
- Cosine similarity-based semantic retrieval
- Stateless API design with explicit reindexing

---
## How It Works

1. Documents are loaded from static files and database
2. Text is chunked and deduplicated
3. Embeddings are generated via external API
4. Stored in an in-memory vector store
5. Query is embedded and matched using cosine similarity
6. Top-k results are passed as context to the LLM
7. Final response is generated and normalized
8. Query and response are logged in the database
---
## Installation and Setup

### 1. Clone repository
```bash
git clone https://github.com/your-username/rag-core.git  
cd RAG_Core_Service
```

## 2. Create virtual environment

```bash
python3 -m venv venv           
source venv/bin/activate
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```
### 4. Environment configuration

Create a `.env` file:

```bash
OPENROUTER_API_KEY=your_api_key
```

Optional:
```
DATABASE_URL=sqlite:///./rag.db
```

---

### 5. Run the application

```
uvicorn main:app --reload
```

Default URL:
```
http://127.0.0.1:8000
```

Interactive documentation:

The API provides automatically generated interactive documentation:

- Swagger UI: 
```
http://127.0.0.1:8000/docs  
```

- ReDoc:  
```
http://127.0.0.1:8000/redoc  
```

These interfaces allow you to explore endpoints, validate request/response schemas, and execute requests directly from the browser.

---

## Testing

**Purpose**  
Provides an automated end-to-end validation of the API, including document lifecycle, indexing, and RAG query behavior. It is intended to verify that the system behaves as expected under both valid and invalid scenarios.

**Usage**

```bash
chmod +x scripts/full_test.sh
./scripts/full_test.sh
```

Optional:

```bash
BASE_URL=http://127.0.0.1:8000 ./scripts/full_test.sh
```

**Output**
- `success.txt` → expected behaviors that passed    
- `errors.txt` → deviations from expected behavior

---
## Extra Notes

- Requires a valid OpenRouter API key for full functionality
- If the API key is missing, embeddings and LLM responses will not work
- The vector store is not persistent and is rebuilt on startup or reindex
- Designed for clarity and extensibility rather than production-scale optimization

