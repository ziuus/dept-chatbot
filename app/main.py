from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.brain import DepartmentBrain, ensure_storage_path
from app.config import settings
from app.logging_utils import RequestContextLoggingMiddleware, configure_logging
from app.models import IngestResponse, QueryRequest, QueryResponse, Source
from app.security import enforce_rate_limit, require_api_key


app = FastAPI(title="Department AI Brain", version="0.1.0")
configure_logging()
app.add_middleware(RequestContextLoggingMiddleware)
ensure_storage_path()
brain = DepartmentBrain()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, object]:
    checks = brain.readiness()
    return {"status": "ok", "checks": checks}


@app.on_event("startup")
def on_startup() -> None:
    settings.validate()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "request_id": request_id},
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest(
    _: None = Depends(require_api_key),
    __: None = Depends(enforce_rate_limit),
) -> IngestResponse:
    try:
        count = brain.ingest_faculty()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return IngestResponse(message="Knowledge base ingested.", chunk_count=count)


@app.post("/query", response_model=QueryResponse)
def query(
    payload: QueryRequest,
    _: None = Depends(require_api_key),
    __: None = Depends(enforce_rate_limit),
) -> QueryResponse:
    if len(payload.question) > settings.max_question_chars:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds max length of {settings.max_question_chars} characters.",
        )
    try:
        answer, route, raw_sources = brain.answer(payload.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    sources = [
        Source(
            id=s["id"],
            text=s["text"],
            metadata=s.get("metadata", {}),
            score=s.get("score"),
        )
        for s in raw_sources
    ]
    return QueryResponse(answer=answer, route=route, sources=sources)
