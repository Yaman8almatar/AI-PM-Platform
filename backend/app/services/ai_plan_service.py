import asyncio
import importlib.util
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict

from app.core.config import get_settings
from app.models.plan_models import PlanOutput

logger = logging.getLogger(__name__)


@lru_cache()
def _load_ai_core_generator() -> Callable[..., Dict[str, Any]]:
    """
    Load ai-core/src/ai_engine.py dynamically so backend can reuse the
    project prompt/schema pipeline without duplicating logic.
    """
    repo_root = Path(__file__).resolve().parents[3]
    ai_engine_path = repo_root / "ai-core" / "src" / "ai_engine.py"

    if not ai_engine_path.exists():
        raise FileNotFoundError(f"AI core engine not found: {ai_engine_path}")

    spec = importlib.util.spec_from_file_location("ai_core_engine", ai_engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec from {ai_engine_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    generate_fn = getattr(module, "generate_project_plan", None)
    if not callable(generate_fn):
        raise AttributeError("generate_project_plan was not found in ai-core engine.")

    return generate_fn


async def generate_ai_plan(request_text: str) -> PlanOutput:
    settings = get_settings()

    try:
        generate_project_plan = _load_ai_core_generator()
        ai_result = await asyncio.to_thread(
            generate_project_plan,
            request_text,
            settings.ai_model_name,
            settings.ai_temperature,
            settings.gemini_api_key or None,
        )
        return PlanOutput(**ai_result)
    except Exception as e:
        logger.error(f"Failed to generate AI plan: {e}")
        raise Exception("Failed to generate plan via ai-core. Check Gemini settings and input.")
