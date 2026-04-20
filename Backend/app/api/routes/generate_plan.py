from fastapi import APIRouter, HTTPException
from app.models.plan_models import GeneratePlanRequest, PlanOutput
from app.services.mock_plan_service import generate_mock_plan
from app.services.ai_plan_service import generate_ai_plan
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-plan", response_model=PlanOutput)
async def generate_plan(request: GeneratePlanRequest):
    try:
        if settings.use_ai_mock:
            logger.info("Using MOCK Plan Service")
            return await generate_mock_plan(request.text)
        else:
            logger.info("Using REAL AI Plan Service")
            return await generate_ai_plan(request.text)
    except Exception as e:
        logger.error(f"Error generation plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))