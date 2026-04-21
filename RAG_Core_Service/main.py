#!/usr/bin/env python3

from fastapi import FastAPI

from api.json_response import UnicodeJSONResponse
from api.routes import router as api_router
from core.dependencies import Base, engine
from infrastructure.persistence.models import Document, QueryLog  # noqa: F401
from infrastructure.persistence.sqlite_migrate import ensure_sqlite_schema


Base.metadata.create_all(bind=engine)
ensure_sqlite_schema(engine)


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Core",
        version="0.1",
        default_response_class=UnicodeJSONResponse,
    )

    app.include_router(api_router)

    return app


app = create_app()
