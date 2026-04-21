#!/usr/bin/env python3

from sqlalchemy import Engine, text


def _sqlite_columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return {r[1] for r in rows}


def ensure_sqlite_schema(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return

    cols = _sqlite_columns(engine, "documents")
    statements: list[str] = []

    if "source" not in cols:
        statements.append(
            "ALTER TABLE documents ADD COLUMN source VARCHAR NOT NULL DEFAULT 'db'"
        )
    if "is_active" not in cols:
        statements.append(
            "ALTER TABLE documents ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
        )
    if "updated_at" not in cols:
        statements.append(
            "ALTER TABLE documents ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )

    # Indexes (safe to run even if columns pre-existed)
    statements.append(
        "CREATE INDEX IF NOT EXISTS ix_documents_is_active ON documents (is_active)"
    )

    if not statements:
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
