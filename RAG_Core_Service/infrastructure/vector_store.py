#!/usr/bin/env python3

import math

from infrastructure.LLM.embedding_client import EmbeddingClient


class VectorStore:
    def __init__(self, embedding_client: EmbeddingClient):
        self._embedding_client = embedding_client
        self.documents: list[str] = []
        self.embeddings: list[list[float]] = []


    def clear(self) -> None:
        self.documents = []
        self.embeddings = []


    def add_documents(self, docs: list[str]) -> None:
        for doc in docs:
            embedding = self._embedding_client.embed(doc)

            if embedding:
                self.documents.append(doc)
                self.embeddings.append(embedding)


    def cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)


    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_embedding = self._embedding_client.embed(query)
        if not query_embedding:
            return []

        scored: list[tuple[str, float]] = []

        for doc, emb in zip(self.documents, self.embeddings):
            score = self.cosine_similarity(query_embedding, emb)
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored[:top_k]]
