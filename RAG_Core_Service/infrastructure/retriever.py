#!/usr/bin/env python3

from core.config import Settings
from core.dependencies import SessionLocal
from domain.models import ContextBlock, Question
from sqlalchemy.orm import Session

from infrastructure.data_loader import load_documents_hybrid
from infrastructure.vector_store import VectorStore
from infrastructure.LLM.embedding_client import EmbeddingClient


class SemanticRetriever:
    def __init__(self, settings: Settings, top_k: int = 8):
        self._top_k = top_k
        embedding_client = EmbeddingClient(settings)
        self._vector_store = VectorStore(embedding_client)
        self._settings = settings
        db = SessionLocal()
        try:
            self.reindex(db)
        finally:
            db.close()

    def retrieve(self, question: Question) -> ContextBlock:
        results = self._vector_store.search(question.text, top_k=self._top_k)
        return ContextBlock(text="\n".join(results))

    def reindex(self, db: Session) -> int:
        documents = load_documents_hybrid(self._settings, db)
        self._vector_store.clear()
        self._vector_store.add_documents(documents)
        return len(self._vector_store.documents)
