import openai
import json
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

async def call_ai_model(prompt: str) -> dict:
    openai.api_key = settings.openai_api_key
    try:
        response = await openai.ChatCompletion.acreate(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a JSON-only project planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
        return data
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        raise e