from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.core.config import settings
from src.models.schemas import (
    HealthResponse,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    Source,
    StatusResponse,
)
from src.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", version="0.1.0")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    pdf_folder = settings.pdf_storage_path
    pdf_folder.mkdir(parents=True, exist_ok=True)

    sanitized_name = Path(file.filename).name
    persisted_path = pdf_folder / f"{uuid4().hex}_{sanitized_name}"
    with persisted_path.open("wb") as out_file:
        out_file.write(await file.read())

    inserted_chunks, metadata = rag_service.ingest_pdf(persisted_path)
    return IngestResponse(
        success=True,
        document_name=file.filename,
        inserted_chunks=inserted_chunks,
        metadata={"document_path": str(persisted_path), "stored_chunks": str(inserted_chunks)},
    )


@router.get("/status", response_model=StatusResponse)
def status():
    current_status = rag_service.status()
    return StatusResponse(**current_status)


@router.post("/query", response_model=QueryResponse)
def query(query_request: QueryRequest):
    answer, hits = rag_service.query(query_request.query, query_request.top_k)
    sources = [Source(text=hit.get("text", ""), metadata={k: v for k, v in hit.items() if k != "text"}) for hit in hits]
    return QueryResponse(query=query_request.query, answer=answer, sources=sources)
