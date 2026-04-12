import json
import os
import logging
from typing import Dict, Any, Optional, List

try:
    from google import genai
except ImportError:
    raise ImportError("google-genai not installed. Run: pip install google-genai")

from app.ai.prompts import get_system_prompt
from app.ai.schema import get_plan_schema

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "gemini-2.5-flash"
AI_TEMPERATURE = 0.1

def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    raise ValueError("GEMINI_API_KEY environment variable not set")

def get_ai_client():
    return genai.Client(api_key=_get_api_key())

async def generate_plan_with_ai(scope_text: str) -> Dict[str, Any]:
    """استدعاء Gemini AI لتوليد الخطة"""
    client = get_ai_client()
    system_prompt = get_system_prompt()
    plan_schema = get_plan_schema()
    
    response = client.models.generate_content(
        model=DEFAULT_MODEL_NAME,
        contents=scope_text,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_json_schema": plan_schema,
            "temperature": AI_TEMPERATURE,
        },
    )
    
    raw_text = response.text.strip()
    try:
        plan = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw: {raw_text}")
    
    errors = validate_ai_plan(plan)
    if errors:
        raise ValueError(f"AI plan validation failed: {errors}")
    
    return plan

def validate_ai_plan(plan: Dict[str, Any]) -> List[str]:
    """التحقق من صحة الخطة المستلمة من AI"""
    errors = []
    
    required_keys = {"project_name", "wbs", "gantt_data", "risk_log"}
    if not required_keys.issubset(plan.keys()):
        missing = required_keys - plan.keys()
        errors.append(f"Missing keys: {missing}")
    
    wbs = plan.get("wbs", [])
    if len(wbs) < 3:
        errors.append("WBS must have at least 3 phases")
    
    for phase in wbs:
        tasks = phase.get("tasks", [])
        if len(tasks) < 3:
            errors.append(f"Phase '{phase.get('phase')}' has fewer than 3 tasks")
    
    if len(plan.get("gantt_data", [])) == 0:
        errors.append("gantt_data cannot be empty")
    
    if len(plan.get("risk_log", [])) == 0:
        errors.append("risk_log cannot be empty")
    
    return errors