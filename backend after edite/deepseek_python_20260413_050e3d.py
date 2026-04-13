import logging
from fastapi import APIRouter, HTTPException, status
from app.models.plan_models import GeneratePlanRequest, GeneratePlanResponse
from app.services.mock_plan_service import generate_mock_plan
from app.services.ai_plan_service import generate_ai_plan
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post(
    "/generate-plan",
    response_model=GeneratePlanResponse,
    status_code=status.HTTP_200_OK,
    summary="توليد خطة مشروع",
    description="يستقبل نطاق المشروع ويعيد خطة منظمة بصيغة JSON"
)
async def generate_plan(request: GeneratePlanRequest):
    try:
        logger.info(f"Received request with text length: {len(request.text)}")
        logger.info(f"Using AI mode: {settings.use_ai_real}")
        
        if settings.use_ai_real:
            # وضع الإنتاج الحقيقي - لا Fallback إلى Mock
            # في حالة الفشل، سيتم إرجاع خطأ مباشرة من ai_plan_service
            result = await generate_ai_plan(request.text)
        else:
            # وضع التطوير - استخدام Mock فقط
            result = await generate_mock_plan(request.text)
        
        logger.info(f"Generated plan_id: {result.plan_id}")
        return result
        
    except HTTPException:
        # إعادة رفع استثناءات HTTP كما هي
        raise
        
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"خطأ داخلي: {str(e)}")