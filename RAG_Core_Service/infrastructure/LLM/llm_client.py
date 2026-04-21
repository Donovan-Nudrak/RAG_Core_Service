#!/usr/bin/env python3

import requests

from core.config import Settings


class LLMClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def complete(self, prompt: str) -> str:
        if not self._settings.openrouter_api_key:
            return "Error: OPENROUTER_API_KEY not configured"

        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._settings.http_referer,
            "X-Title": self._settings.app_title_header,
        }

        payload = {
            "model": self._settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self._settings.llm_temperature,
            "top_p": self._settings.llm_top_p,
        }
        if self._settings.llm_frequency_penalty > 0:
            payload["frequency_penalty"] = self._settings.llm_frequency_penalty

        response = requests.post(
            self._settings.openrouter_chat_url,
            json=payload,
            headers=headers,
            timeout=120,
        )

        if response.status_code != 200:
            return "Error comunication with LLM"

        data = response.json()
        return data["choices"][0]["message"]["content"]
