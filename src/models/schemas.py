from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field("ok")
    version: str


class StatusResponse(BaseModel):
    vector_count: int
    embedding_model: str
    openai_enabled: bool
    index_type: str


class IngestResponse(BaseModel):
    success: bool
    document_name: str
    inserted_chunks: int
    metadata: Dict[str, str] = {}


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class Source(BaseModel):
    text: str
    metadata: Dict[str, str]


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source]
