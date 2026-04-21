#!/usr/bin/env python3

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.schemas import (
    AnswerResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    QuestionRequest,
)
from core.container import get_rag_service, get_retriever
from core.dependencies import get_db
from infrastructure.persistence.models import Document
from infrastructure.retriever import SemanticRetriever
from services.rag_service import RAGService
from utils.text_normalize import normalize_answer_text

router = APIRouter()

@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    rag: RAGService = Depends(get_rag_service),
):
    answer = rag.process(request.question, db)
    return AnswerResponse(answer=normalize_answer_text(answer))


@router.post("/documents/reindex")
def reindex_documents(
    db: Session = Depends(get_db),
    retriever: SemanticRetriever = Depends(get_retriever),
):
    indexed = retriever.reindex(db)
    return {"indexed_documents": indexed}


@router.post("/documents", response_model=DocumentResponse)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content must not be empty")

    doc = Document(
        title=(payload.title.strip() if payload.title else None),
        content=content,
        source="db",
        is_active=True,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = select(Document).order_by(Document.id.asc())
    if not include_inactive:
        stmt = stmt.where(Document.is_active.is_(True))
    return list(db.execute(stmt).scalars())


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


@router.put("/documents/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")

    if payload.title is not None:
        doc.title = payload.title.strip() or None
    if payload.content is not None:
        content = payload.content.strip()
        if not content:
            raise HTTPException(status_code=400, detail="content must not be empty")
        doc.content = content
    if payload.is_active is not None:
        doc.is_active = payload.is_active

    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    doc.is_active = False
    db.add(doc)
    db.commit()
    return {"ok": True}
