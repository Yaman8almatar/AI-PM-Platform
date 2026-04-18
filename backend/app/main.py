import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.plan import router as plan_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for AI-based Project Planning Automation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router, prefix="/api", tags=["Plan"])


@app.get("/", summary="Root")
async def root():
    return {
        "message": "AI PM Platform Backend is running.",
        "docs": "/docs",
    }


@app.get("/health", summary="Health check")
async def health():
    repo_root = Path(__file__).resolve().parents[2]
    ai_core_path = repo_root / "ai-core"

    return {
        "status": "ok",
        "mode": "real-ai",
        "model": settings.ai_model_name,
        "gemini_api_key_configured": bool(settings.gemini_api_key),
        "ai_core_exists": ai_core_path.exists(),
    }
