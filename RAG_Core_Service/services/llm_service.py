#!/usr/bin/env python3

from core.config import Settings
from domain.models import Answer, ContextBlock, Question
from infrastructure.LLM.llm_client import LLMClient


class LLMAnswerGenerator:
    def __init__(self, settings: Settings):
        self._client = LLMClient(settings)

    def generate(self, question: Question, context: ContextBlock) -> Answer:
        ctx = context.text.strip()
        ctx_block = ctx if ctx else "(context not found)"

        prompt = f"""You are a technical assistant. Always respond in clear and complete English.

Format: use only standard Latin alphabet, numbers, and punctuation. Avoid unusual symbols or non-Latin scripts.

Use the following CONTEXT as the only source of truth. You may summarize and reformulate, but do not invent information.

If the context is empty or not relevant, respond exactly: Not found

Context:
{ctx_block}

Question:
{question.text}
"""
        text = self._client.complete(prompt)
        return Answer(text=text.strip())
