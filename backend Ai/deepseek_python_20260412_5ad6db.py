import asyncio
from datetime import datetime
import logging
from app.models.plan_models import GeneratePlanResponse, PlanOutput, WBSPhase, GanttTask, RiskItem
from app.ai.engine import generate_plan_with_ai
from app.services.mock_plan_service import generate_mock_plan
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def generate_ai_plan(request_text: str) -> GeneratePlanResponse:
    try:
        logger.info("Calling Gemini AI for plan generation")
        ai_result = await generate_plan_with_ai(request_text)
        
        plan = PlanOutput(
            project_name=ai_result["project_name"],
            wbs=[WBSPhase(**phase) for phase in ai_result["wbs"]],
            gantt_data=[GanttTask(**task) for task in ai_result["gantt_data"]],
            risk_log=[RiskItem(**risk) for risk in ai_result["risk_log"]]
        )
        
        return GeneratePlanResponse(
            plan=plan,
            generated_at=datetime.utcnow().isoformat(),
            model_used="gemini-ai"
        )
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}, falling back to mock")
        logger.info("Using mock plan as fallback")
        return await generate_mock_plan(request_text)