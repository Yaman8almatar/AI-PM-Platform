from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from google import genai
except Exception as e:
    raise ImportError(
        "google-genai is not installed. Install it with: pip install -U google-genai"
    ) from e


BASE_DIR = Path(__file__).resolve().parents[1]
PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt_final.txt"
SCHEMA_PATH = BASE_DIR / "schema" / "plan_schema_final.json"
DEFAULT_MODEL_NAME = "gemini-2.5-flash"


def _get_api_key(explicit_api_key: Optional[str] = None) -> str:
    if explicit_api_key:
        return explicit_api_key

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key

    try:
        from google.colab import userdata  # type: ignore
        secret_key = userdata.get("GEMINI_API_KEY")
        if secret_key:
            return secret_key
    except Exception:
        pass

    raise ValueError(
        "GEMINI_API_KEY not found. Set it in environment variables or in Colab Secrets."
    )


def _load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def get_client(api_key: Optional[str] = None):
    return genai.Client(api_key=_get_api_key(api_key))


def get_system_prompt() -> str:
    return _load_text(PROMPT_PATH)


def get_plan_schema() -> Dict[str, Any]:
    return _load_json(SCHEMA_PATH)


def validate_plan(plan: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required_top_keys = {"project_name", "wbs", "gantt_data", "risk_log"}
    actual_top_keys = set(plan.keys())

    if actual_top_keys != required_top_keys:
        missing = sorted(required_top_keys - actual_top_keys)
        extra = sorted(actual_top_keys - required_top_keys)
        if missing:
            errors.append(f"Missing top-level keys: {missing}")
        if extra:
            errors.append(f"Extra top-level keys: {extra}")

    wbs_task_names = set()
    if isinstance(plan.get("wbs"), list):
        for i, phase in enumerate(plan["wbs"], start=1):
            if not isinstance(phase, dict):
                errors.append(f"WBS item #{i} is not an object.")
                continue

            phase_name = phase.get("phase", f"phase_{i}")
            tasks = phase.get("tasks")

            if not isinstance(tasks, list) or len(tasks) == 0:
                errors.append(f"WBS phase '{phase_name}' must have at least one task.")
                continue

            for task in tasks:
                if not isinstance(task, str) or not task.strip():
                    errors.append(f"WBS phase '{phase_name}' contains an invalid task.")
                else:
                    wbs_task_names.add(task.strip())

    gantt_task_names = set()
    gantt_items = plan.get("gantt_data")
    if isinstance(gantt_items, list):
        for i, item in enumerate(gantt_items, start=1):
            if not isinstance(item, dict):
                errors.append(f"Gantt item #{i} is not an object.")
                continue

            task_name = item.get("task_name")
            duration_days = item.get("duration_days")
            dependencies = item.get("dependencies")

            if not isinstance(task_name, str) or not task_name.strip():
                errors.append(f"Gantt item #{i} has invalid task_name.")
                continue

            if task_name in gantt_task_names:
                errors.append(f"Duplicate Gantt task_name: {task_name}")
            gantt_task_names.add(task_name)

            if task_name not in wbs_task_names:
                errors.append(f"Gantt task '{task_name}' does not exist in WBS.")

            if not isinstance(duration_days, int) or duration_days < 1:
                errors.append(f"Gantt task '{task_name}' has invalid duration_days.")

            if not isinstance(dependencies, list):
                errors.append(f"Gantt task '{task_name}' must have a dependencies array.")

    if isinstance(gantt_items, list):
        for item in gantt_items:
            task_name = item.get("task_name", "")
            dependencies = item.get("dependencies", [])
            if isinstance(dependencies, list):
                for dep in dependencies:
                    if dep not in gantt_task_names:
                        errors.append(f"Task '{task_name}' depends on non-existing task '{dep}'.")
                    if dep == task_name:
                        errors.append(f"Task '{task_name}' cannot depend on itself.")

    valid_levels = {"Low", "Medium", "High"}
    if isinstance(plan.get("risk_log"), list):
        for i, risk in enumerate(plan["risk_log"], start=1):
            if not isinstance(risk, dict):
                errors.append(f"Risk item #{i} is not an object.")
                continue

            if risk.get("probability") not in valid_levels:
                errors.append(f"Risk item #{i} has invalid probability.")
            if risk.get("impact") not in valid_levels:
                errors.append(f"Risk item #{i} has invalid impact.")

    return errors


def generate_project_plan(
    scope_text: str,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: float = 0.1,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(scope_text, str) or not scope_text.strip():
        raise ValueError("scope_text must be a non-empty string.")

    client = get_client(api_key)
    system_prompt = get_system_prompt()
    plan_schema = get_plan_schema()

    response = client.models.generate_content(
        model=model_name,
        contents=scope_text,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_json_schema": plan_schema,
            "temperature": temperature,
        },
    )

    raw_text = response.text.strip()

    try:
        plan = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON. Raw output:\n{raw_text}\n\nError: {e}"
        ) from e

    errors = validate_plan(plan)
    if errors:
        raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

    return plan


def save_plan(plan: Dict[str, Any], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    demo_scope = "نظام لإدارة المؤتمرات الجامعية يسمح بالتسجيل وتنظيم الفعاليات."
    plan = generate_project_plan(demo_scope)
    save_plan(plan, BASE_DIR / "outputs" / "final_project_plan_output.json")
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
