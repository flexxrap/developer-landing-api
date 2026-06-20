import json
import logging
import re

import httpx

from app.config import settings

_logger = logging.getLogger("ai")
_TIMEOUT = 10.0
_MODEL = "mistralai/mistral-7b-instruct:free"

_PROMPT = (
    "Analyze the following message and respond ONLY with valid JSON "
    "in this exact format (no markdown, no extra text):\n"
    '{"sentiment": "positive|neutral|negative|urgent", '
    '"type": "question|feedback|complaint|partnership", '
    '"priority": "low|medium|high"}\n\n'
    "Message: {comment}"
)


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[^}]+\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON found in: {text!r}")


async def analyze_comment(comment: str) -> dict | None:
    if not settings.openrouter_api_key:
        _logger.warning("OPENROUTER_API_KEY not set, skipping AI analysis")
        return None

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": _MODEL,
                    "messages": [
                        {"role": "user", "content": _PROMPT.format(comment=comment)}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 100,
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            return _extract_json(raw)
    except Exception as exc:
        _logger.error("AI analysis failed: %s", exc)
        return None
