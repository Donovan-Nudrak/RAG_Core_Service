#!/usr/bin/env python3

import json
import os
import re
import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import Settings
from infrastructure.persistence.models import Document

_MAX_CHUNK_CHARS = 850

_WHITESPACE_RE = re.compile(r"\s+")

def _split_long(text: str, max_chars: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + max_chars].strip())
        start += max_chars
    return [c for c in chunks if c]


def chunk_text(text: str, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return _split_long(text, max_chars) if len(text) > max_chars else [text]

    out: list[str] = []
    for p in paragraphs:
        if len(p) <= max_chars:
            out.append(p)
        else:
            out.extend(_split_long(p, max_chars))
    return out


def _normalize_for_dedup(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_documents(settings: Settings) -> list[str]:
    documents: list[str] = []
    data_path: Path = settings.data_path
    if not data_path.is_dir():
        return documents

    for file in sorted(os.listdir(data_path)):
        path = data_path / file

        if file.endswith(".txt"):
            with open(path, encoding="utf-8") as f:
                documents.extend(chunk_text(f.read()))

        elif file.endswith(".json"):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    line = f"{item.get('title', '')}: {item.get('content', '')}"
                    documents.extend(chunk_text(line))

    return documents


def load_documents_from_db(db: Session) -> list[str]:
    rows = db.execute(
        select(Document).where(Document.is_active.is_(True)).order_by(Document.id.asc())
    ).scalars()

    documents: list[str] = []
    for doc in rows:
        title = (doc.title or "").strip()
        content = doc.content.strip()
        if not content:
            continue
        if title:
            documents.extend(chunk_text(f"{title}: {content}"))
        else:
            documents.extend(chunk_text(content))
    return documents


def load_documents_hybrid(settings: Settings, db: Session) -> list[str]:
    combined = load_documents(settings) + load_documents_from_db(db)

    seen: set[str] = set()
    out: list[str] = []
    for raw in combined:
        normalized = _normalize_for_dedup(raw)
        if not normalized:
            continue
        key = _sha256(normalized)
        if key in seen:
            continue
        seen.add(key)
        out.append(raw)
    return out
