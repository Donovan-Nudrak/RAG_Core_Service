#!/usr/bin/env python3

from typing import Protocol

from domain.models import Answer, ContextBlock, Question


class ContextRetriever(Protocol):
    def retrieve(self, question: Question) -> ContextBlock: ...


class AnswerGenerator(Protocol):
    def generate(self, question: Question, context: ContextBlock) -> Answer: ...
