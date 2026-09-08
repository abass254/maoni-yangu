import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, ensure_schema
from .routers import auth, surveys
from .seed import ensure_superadmin

Base.metadata.create_all(bind=engine)
ensure_schema()
ensure_superadmin()

app = FastAPI(title="Maoni Yangu API", version="1.0.0")

_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:7200",
    "http://127.0.0.1:7200",
]


def _cors_origins() -> list[str]:
    """Local defaults plus comma-separated CORS_ORIGINS (e.g. your Vercel URL)."""
    extra = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    # Preserve order, drop duplicates
    seen: set[str] = set()
    origins: list[str] = []
    for origin in _DEFAULT_ORIGINS + extra:
        if origin not in seen:
            seen.add(origin)
            origins.append(origin)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    # Preview + production Vercel URLs without manual CORS_ORIGINS updates
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(surveys.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"ok": True}
