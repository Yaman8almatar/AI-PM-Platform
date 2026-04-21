from app.models.plan_models import PlanOutput, WBSPhase, GanttTask, RiskEntry

async def generate_mock_plan(request_text: str) -> PlanOutput:
    return PlanOutput(
        project_name="نظام إدارة مشاريع ذكي (Mock)",
        wbs=[
            WBSPhase(phase="1. التحليل", tasks=["جمع المتطلبات", "تحليل النطاق"]),
            WBSPhase(phase="2. التصميم", tasks=["تصميم قواعد البيانات", "تصميم الواجهات"]),
            WBSPhase(phase="3. التنفيذ", tasks=["برمجة الخلفية", "برمجة الواجهات"])
        ],
        gantt_data=[
            GanttTask(task_name="جمع المتطلبات", duration_days=3, dependencies=[]),
            GanttTask(task_name="تحليل النطاق", duration_days=2, dependencies=["جمع المتطلبات"]),
            GanttTask(task_name="تصميم قواعد البيانات", duration_days=4, dependencies=["تحليل النطاق"]),
            GanttTask(task_name="تصميم الواجهات", duration_days=4, dependencies=["تحليل النطاق"]),
            GanttTask(task_name="برمجة الخلفية", duration_days=7, dependencies=["تصميم قواعد البيانات"]),
            GanttTask(task_name="برمجة الواجهات", duration_days=6, dependencies=["تصميم الواجهات"])
        ],
        risk_log=[
            RiskEntry(
                risk="تأخر العميل في تسليم المتطلبات",
                probability="High", impact="High",
                mitigation="عقد اجتماعات يومية وتوثيق المتطلبات فوراً"
            ),
            RiskEntry(
                risk="صعوبة في دمج مكتبات الواجهة",
                probability="Medium", impact="Medium",
                mitigation="عمل اختبار تقني مبكر للمكتبة (PoC)"
            )
        ]
    )