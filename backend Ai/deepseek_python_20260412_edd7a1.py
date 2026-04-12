import uuid
import asyncio
from datetime import datetime
from app.models.plan_models import (
    GeneratePlanResponse, PlanOutput, WBSPhase, GanttTask, RiskItem
)
from app.core.config import get_settings

settings = get_settings()

async def generate_mock_plan(request_text: str) -> GeneratePlanResponse:
    if settings.mock_response_delay_seconds > 0:
        await asyncio.sleep(settings.mock_response_delay_seconds)
    
    project_name = request_text[:50] + ("..." if len(request_text) > 50 else "")
    
    plan = PlanOutput(
        project_name=project_name,
        wbs=[
            WBSPhase(phase="1. التحليل", tasks=["فهم المتطلبات", "دراسة الجدوى", "تحليل المخاطر"]),
            WBSPhase(phase="2. التصميم", tasks=["تصميم قاعدة البيانات", "تصميم الواجهات", "تصميم API"]),
            WBSPhase(phase="3. التنفيذ", tasks=["تطوير الـ Backend", "بناء الواجهات", "اختبار الوحدة"]),
        ],
        gantt_data=[
            GanttTask(task_name="فهم المتطلبات", duration_days=3, dependencies=[]),
            GanttTask(task_name="تصميم قاعدة البيانات", duration_days=5, dependencies=["فهم المتطلبات"]),
            GanttTask(task_name="تطوير الـ Backend", duration_days=10, dependencies=["تصميم قاعدة البيانات"]),
        ],
        risk_log=[
            RiskItem(risk="تأخر تسليم المتطلبات", probability="Medium", impact="High"),
            RiskItem(risk="مشكلة في التكامل", probability="Low", impact="Medium"),
        ]
    )
    
    return GeneratePlanResponse(
        plan=plan,
        generated_at=datetime.utcnow().isoformat(),
        model_used="mock"
    )