#!/usr/bin/env python3

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


class DocumentCreate(BaseModel):
    title: str | None = None
    content: str


class DocumentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_active: bool | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str | None
    content: str
    source: str
    is_active: bool

