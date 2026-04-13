import asyncio
import sys
import os
from datetime import datetime
import logging
from fastapi import HTTPException

# إضافة مسار ai-core إلى sys.path
# افتراض أن هيكل المشروع كالتالي:
# project-backend/
#   app/
#   ai-core/   (مجلد عمر العساف)
#       src/
#           ai_engine.py
#       prompts/
#       schema/

AI_CORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai-core'))
if AI_CORE_PATH not in sys.path:
    sys.path.insert(0, AI_CORE_PATH)

# استيراد دالة عمر الأصلية
try:
    from src.ai_engine import generate_project_plan
except ImportError as e:
    raise ImportError(
        f"Failed to import from ai-core. Make sure ai-core folder exists at: {AI_CORE_PATH}\nError: {e}"
    )

from app.models.plan_models import GeneratePlanResponse, PlanOutput, WBSPhase, GanttTask, RiskItem

logger = logging.getLogger(__name__)

# مهلة الـ AI بالثواني
AI_TIMEOUT_SECONDS = 30.0


async def generate_ai_plan(request_text: str) -> GeneratePlanResponse:
    """
    استدعاء محرك AI الخاص بعمر العساف مع معالجة المهلة (Timeout)
    في حالة الفشل، يتم إرجاع خطأ صريح (لا Fallback إلى Mock)
    """
    try:
        logger.info(f"Calling Omar's AI engine for plan generation. Timeout: {AI_TIMEOUT_SECONDS}s")
        
        # generate_project_plan هي دالة متزامنة (sync)
        # نستخدم asyncio.to_thread لتحويلها إلى async مع مهلة محددة
        ai_result = await asyncio.wait_for(
            asyncio.to_thread(generate_project_plan, request_text),
            timeout=AI_TIMEOUT_SECONDS
        )
        
        logger.info("AI response received successfully")
        
        # تحويل النتيجة إلى نموذج Pydantic
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
        
    except asyncio.TimeoutError:
        logger.error(f"AI request timed out after {AI_TIMEOUT_SECONDS} seconds")
        raise HTTPException(
            status_code=504,
            detail=f"تأخر استجابة الذكاء الاصطناعي (Timeout بعد {AI_TIMEOUT_SECONDS} ثانية)"
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطأ في تهيئة محرك الذكاء الاصطناعي: {str(e)}"
        )
        
    except ValueError as e:
        logger.error(f"Validation error from AI: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"البيانات المرجعة من الذكاء الاصطناعي غير صالحة: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"فشل في توليد الخطة: {str(e)}"
        )