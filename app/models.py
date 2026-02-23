from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, description="User question")


class Source(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    route: str
    sources: list[Source]


class IngestResponse(BaseModel):
    message: str
    chunk_count: int
