from pydantic import BaseModel
from typing import List

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