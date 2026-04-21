#!/usr/bin/env python3

import requests

from core.config import Settings


class EmbeddingClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def embed(self, text: str) -> list[float]:
        if not self._settings.openrouter_api_key:
            return []

        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._settings.embedding_model,
            "input": text,
        }

        response = requests.post(
            self._settings.openrouter_embeddings_url,
            json=payload,
            headers=headers,
            timeout=120,
        )

        if response.status_code != 200:
            return []

        data = response.json()
        return data["data"][0]["embedding"]
