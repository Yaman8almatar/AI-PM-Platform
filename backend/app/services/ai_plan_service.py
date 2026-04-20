import asyncio
import logging
import sys
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.models.plan_models import PlanOutput, WBSPhase, GanttTask, RiskItem

logger = logging.getLogger(__name__)
settings = get_settings()

# backend/app/services/ai_plan_service.py
# parents[0] = services
# parents[1] = app
# parents[2] = backend
# parents[3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
AI_CORE_PATH = REPO_ROOT / "ai-core"

if str(AI_CORE_PATH) not in sys.path:
    sys.path.insert(0, str(AI_CORE_PATH))

try:
    from src.ai_engine import generate_project_plan
except ImportError as exc:
    raise ImportError(
        f"Failed to import ai-core from path: {AI_CORE_PATH}. Error: {exc}"
    ) from exc


def _ensure_ai_core_layout() -> None:
    required_paths = [
        AI_CORE_PATH / "src" / "ai_engine.py",
        AI_CORE_PATH / "prompts" / "system_prompt_final.txt",
        AI_CORE_PATH / "schema" / "plan_schema_final.json",
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Required ai-core file not found: {path}")


async def generate_ai_plan(scope_text: str) -> PlanOutput:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="لم يتم ضبط GEMINI_API_KEY داخل ملف .env",
        )

    try:
        _ensure_ai_core_layout()

        raw_result = await asyncio.wait_for(
            asyncio.to_thread(
                generate_project_plan,
                scope_text,
                settings.ai_model_name,
                settings.ai_temperature,
                settings.gemini_api_key,
            ),
            timeout=settings.ai_timeout_seconds,
        )

        if not isinstance(raw_result, dict):
            raise ValueError("استجابة ai-core ليست كائن JSON صالحًا.")

        plan = PlanOutput(
            project_name=raw_result["project_name"],
            wbs=[WBSPhase(**phase) for phase in raw_result["wbs"]],
            gantt_data=[GanttTask(**task) for task in raw_result["gantt_data"]],
            risk_log=[RiskItem(**risk) for risk in raw_result["risk_log"]],
        )

        return plan

    except asyncio.TimeoutError:
        logger.error("AI request timed out after %s seconds", settings.ai_timeout_seconds)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"تجاوزت استجابة الذكاء الاصطناعي المهلة المحددة ({settings.ai_timeout_seconds} ثانية).",
        )

    except FileNotFoundError as exc:
        logger.error("Missing ai-core file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ملف مطلوب داخل ai-core غير موجود: {exc}",
        )

    except KeyError as exc:
        logger.error("Missing expected key from ai-core response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"الاستجابة المرجعة من ai-core ناقصة. المفتاح المفقود: {exc}",
        )

    except ValueError as exc:
        logger.error("Validation failed for AI output: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"البيانات المرجعة من الذكاء الاصطناعي غير صالحة: {exc}",
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Unexpected AI generation failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل داخلي أثناء توليد الخطة: {exc}",
        )
