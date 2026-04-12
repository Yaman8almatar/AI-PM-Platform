from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.generate_plan import router
from app.core.config import get_settings
from app.core.logging_config import setup_logging

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(
    title="Project Planning API",
    description="API لتوليد خطط المشاريع - يدعم Mock و AI (Gemini)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_v1_prefix)

@app.get("/health")
async def health_check():
    return {
        "status": "alive",
        "environment": settings.environment,
        "ai_enabled": settings.use_ai_real,
        "ai_ready": bool(settings.gemini_api_key)
    }

@app.get("/")
async def root():
    return {"message": "Project Planning API", "docs": "/docs"}