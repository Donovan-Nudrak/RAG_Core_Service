#!/usr/bin/env python3

from sqlalchemy.orm import Session

from domain.interfaces import AnswerGenerator, ContextRetriever
from domain.models import Answer, ContextBlock, Question
from infrastructure.persistence.models import QueryLog


class RAGService:
    def __init__(self, retriever: ContextRetriever, generator: AnswerGenerator):
        self._retriever = retriever
        self._generator = generator

    def process(self, question_text: str, db: Session) -> str:
        question = Question(text=question_text)
        context = self._retrieve(question)
        answer = self._generate(question, context)
        self._persist_query_log(db, question, answer)
        return answer.text

    def _retrieve(self, question: Question) -> ContextBlock:
        return self._retriever.retrieve(question)

    def _generate(self, question: Question, context: ContextBlock) -> Answer:
        return self._generator.generate(question, context)

    def _persist_query_log(
        self, db: Session, question: Question, answer: Answer
    ) -> None:
        db.add(QueryLog(question=question.text, answer=answer.text))
        db.commit()


