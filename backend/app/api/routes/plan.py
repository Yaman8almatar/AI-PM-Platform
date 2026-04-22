from fastapi import APIRouter, status

from app.models.plan_models import GeneratePlanRequest, PlanOutput
from app.services.ai_plan_service import generate_ai_plan

router = APIRouter()


@router.post(
    "/generate-plan",
    response_model=PlanOutput,
    status_code=status.HTTP_200_OK,
    summary="Generate project plan",
    description="يستقبل وصف المشروع ويعيد خطة منظمة بصيغة JSON متوافقة مع الواجهة.",
)
async def generate_plan(request: GeneratePlanRequest) -> PlanOutput:
    return await generate_ai_plan(request.text)
