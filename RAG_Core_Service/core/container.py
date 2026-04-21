#!/usr/bin/env python3

from functools import lru_cache

from core.config import get_settings
from infrastructure.retriever import SemanticRetriever
from services.llm_service import LLMAnswerGenerator
from services.rag_service import RAGService


@lru_cache
def get_retriever() -> SemanticRetriever:
    settings = get_settings()
    return SemanticRetriever(settings)


@lru_cache
def get_rag_service() -> RAGService:
    settings = get_settings()
    retriever = get_retriever()
    generator = LLMAnswerGenerator(settings)
    return RAGService(retriever=retriever, generator=generator)
