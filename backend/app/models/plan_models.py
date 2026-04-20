from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class GeneratePlanRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("النص المدخل فارغ.")
        if len(normalized) < 10:
            raise ValueError("وصف المشروع قصير جدًا. أدخل وصفًا أوضح.")
        return normalized


class WBSPhase(BaseModel):
    phase: str = Field(..., min_length=1)
    tasks: list[str] = Field(..., min_length=1)

    @field_validator("phase")
    @classmethod
    def validate_phase(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("اسم المرحلة داخل WBS غير صالح.")
        return normalized

    @field_validator("tasks")
    @classmethod
    def validate_tasks(cls, value: list[str]) -> list[str]:
        cleaned = []
        for task in value:
            if isinstance(task, str):
                normalized = " ".join(task.split())
                if normalized:
                    cleaned.append(normalized)

        if not cleaned:
            raise ValueError("قائمة المهام داخل WBS فارغة أو غير صالحة.")
        return cleaned


class GanttTask(BaseModel):
    task_name: str = Field(..., min_length=1)
    duration_days: int = Field(..., ge=1)
    dependencies: list[str] = Field(default_factory=list)

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("اسم مهمة Gantt غير صالح.")
        return normalized

    @field_validator("dependencies")
    @classmethod
    def validate_dependencies(cls, value: list[str]) -> list[str]:
        cleaned = []
        for dep in value:
            if isinstance(dep, str):
                normalized = " ".join(dep.split())
                if normalized:
                    cleaned.append(normalized)
        return cleaned


class RiskItem(BaseModel):
    risk: str = Field(..., min_length=1)
    probability: Literal["Low", "Medium", "High"]
    impact: Literal["Low", "Medium", "High"]
    mitigation: str = Field(..., min_length=1)

    @field_validator("risk", "mitigation")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("وصف الخطر أو خطة التخفيف غير صالح.")
        return normalized


class PlanOutput(BaseModel):
    project_name: str = Field(..., min_length=1)
    wbs: list[WBSPhase] = Field(..., min_length=1)
    gantt_data: list[GanttTask] = Field(..., min_length=1)
    risk_log: list[RiskItem] = Field(..., min_length=1)

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("اسم المشروع غير صالح.")
        return normalized

    @model_validator(mode="after")
    def validate_cross_structure(self):
        wbs_task_names = set()
        for phase in self.wbs:
            for task in phase.tasks:
                wbs_task_names.add(task)

        gantt_task_names = set()
        for task in self.gantt_data:
            if task.task_name in gantt_task_names:
                raise ValueError(f"اسم المهمة مكرر في Gantt: {task.task_name}")
            gantt_task_names.add(task.task_name)

            if task.task_name not in wbs_task_names:
                raise ValueError(
                    f"مهمة Gantt '{task.task_name}' غير موجودة داخل WBS."
                )

        for task in self.gantt_data:
            for dep in task.dependencies:
                if dep not in gantt_task_names:
                    raise ValueError(
                        f"الاعتماد '{dep}' في المهمة '{task.task_name}' غير موجود ضمن Gantt."
                    )
                if dep == task.task_name:
                    raise ValueError(
                        f"المهمة '{task.task_name}' لا يمكن أن تعتمد على نفسها."
                    )

        return self
