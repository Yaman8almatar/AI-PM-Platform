from pydantic import BaseModel, Field, field_validator
from typing import List
from pydantic import BaseModel, Field, field_validator

class GeneratePlanRequest(BaseModel):
    text: str

class WBSPhase(BaseModel):
    phase: str
    tasks: List[str]

class GanttTask(BaseModel):
    task_name: str
    duration_days: int
    dependencies: List[str] = []

class RiskEntry(BaseModel):
    risk: str
    probability: str
    impact: str
    mitigation: str

class PlanOutput(BaseModel):
    project_name: str
    wbs: List[WBSPhase]
    gantt_data: List[GanttTask]
    risk_log: List[RiskEntry]
    

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