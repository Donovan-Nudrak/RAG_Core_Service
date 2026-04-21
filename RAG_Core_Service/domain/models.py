#!/usr/bin/env python3

from pydantic import BaseModel, Field


class Question(BaseModel):
    text: str = Field(min_length=1)


class ContextBlock(BaseModel):
    text: str


class Answer(BaseModel):
    text: str
