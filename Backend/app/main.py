from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.generate_plan import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="AI PM Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_v1_prefix)

@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": settings.use_ai_mock}