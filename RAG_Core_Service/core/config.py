#!/usr/bin/env python3

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

_APP_ROOT = Path(__file__).resolve().parent.parent

_ENV_FILE = _APP_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./rag.db"

    openrouter_api_key: str = OPENROUTER_API_KEY
    openrouter_chat_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_embeddings_url: str = "https://openrouter.ai/api/v1/embeddings"

    llm_model: str = "meta-llama/llama-3-8b-instruct"
    embedding_model: str = "text-embedding-3-small"

    llm_temperature: float = 0.35
    llm_top_p: float = 0.9
    llm_frequency_penalty: float = 0.0

    data_path: Path = _APP_ROOT / "data"

    http_referer: str = "http://localhost"
    app_title_header: str = "rag-core"


@lru_cache
def get_settings() -> Settings:
    return Settings()
