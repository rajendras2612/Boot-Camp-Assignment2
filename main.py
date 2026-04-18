from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router
from src.core.config import settings
from src.core.logger import logger, setup_logging

setup_logging()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
    openapi_url="/openapi.json",
)
app.include_router(router)

static_path = Path(__file__).resolve().parent / "src" / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Incoming request %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "Completed %s %s with status %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/", tags=["Root"])
def index():
    return {"message": "Multimodal RAG API is running"}


@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
def app_ui():
    return FileResponse(static_path / "index.html")


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def docs_landing():
    return """
    <html>
        <head>
            <title>API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                a { color: #1f77b4; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Multimodal RAG API Documentation</h1>
            <p>Use one of the available documentation interfaces:</p>
            <ul>
                <li><a href="/docs/swagger">Swagger UI</a></li>
                <li><a href="/docs/redoc">ReDoc</a></li>
            </ul>
            <p>OpenAPI schema is available at <code>/openapi.json</code>.</p>
        </body>
    </html>
    """
