"""Smart ingredient substitution suggestions."""

import json
import logging
from typing import Any
from core.llm import get_llm

logger = logging.getLogger("nourishai.substitution")

SUB_PROMPT = """Suggest 3 substitutions for "{ingredient}" (reason: {reason}).
Dietary context: {diets}
Return JSON array:
[{{"name": "substitute", "similarity": 0.0-1.0, "notes": "why this works", "ratio": "1 cup = X cup"}}]
No markdown fences. JSON only."""


async def substitution_suggest(ingredient: str, reason: str = "unavailable", dietary_context: list | None = None) -> dict[str, Any]:
    llm = get_llm(temperature=0.4)
    prompt = SUB_PROMPT.format(ingredient=ingredient, reason=reason, diets=", ".join(dietary_context) if dietary_context else "none")
    response = await llm.ainvoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        subs = json.loads(text)
    except json.JSONDecodeError:
        subs = [{"name": f"{ingredient} alternative", "similarity": 0.5, "notes": "Generic substitute", "ratio": "1:1"}]
    return {"original": ingredient, "reason": reason, "substitutions": sorted(subs, key=lambda x: x.get("similarity", 0), reverse=True)}