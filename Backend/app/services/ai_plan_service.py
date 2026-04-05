from app.core.ai_client import call_ai_model
from app.models.plan_models import PlanOutput
import logging

logger = logging.getLogger(__name__)

async def generate_ai_plan(request_text: str) -> PlanOutput:
    try:
        # هنا سيتم دمج البرومبت الخاص بـ "عمر" لاحقاً
        ai_result = await call_ai_model(f"قم بتحليل النطاق التالي وإرجاع JSON فقط: {request_text}")
        
        # تحويل الـ JSON المرتجع مباشرة إلى النموذج المعتمد
        return PlanOutput(**ai_result)
    except Exception as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise Exception("فشل في توليد الخطة عبر الذكاء الاصطناعي أو أن الهيكل غير مطابق.")