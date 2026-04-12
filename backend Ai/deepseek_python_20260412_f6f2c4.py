from pydantic import BaseModel, Field, field_validator
from typing import List
import uuid

class RiskItem(BaseModel):
    risk: str
    probability: str
    impact: str

class GanttTask(BaseModel):
    task_name: str
    duration_days: int
    dependencies: List[str] = []

class WBSPhase(BaseModel):
    phase: str
    tasks: List[str]

class PlanOutput(BaseModel):
    project_name: str
    wbs: List[WBSPhase]
    gantt_data: List[GanttTask]
    risk_log: List[RiskItem]

class GeneratePlanRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)

    @field_validator("text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("النص لا يمكن أن يكون فارغاً")
        return v.strip()

class GeneratePlanResponse(BaseModel):
    status: str = "success"
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan: PlanOutput
    generated_at: str
    model_used: str