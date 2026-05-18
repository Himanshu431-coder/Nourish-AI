"""Vision-powered pantry scanning via multimodal LLM."""

import json
import logging
from typing import Any
from core.llm import get_vision_llm

logger = logging.getLogger("nourishai.pantry_scan")

PROMPT = """You are a precision ingredient detection system.
Analyze this image and identify ALL visible food ingredients.
For each ingredient provide:
1. "name": Standard name (e.g., "chicken breast", "red bell pepper")
2. "confidence": 0.0-1.0
3. "quantity": Estimated (e.g., "2 pieces", "1 bunch", "500g")
4. "freshness": "fresh" | "good" | "aging" | "expire_soon" | "spoiled"
5. "category": "protein" | "vegetable" | "fruit" | "dairy" | "grain" | "spice" | "other"
Context: this image is from a {context}.
Only include items with confidence >= 0.7.
Return ONLY a JSON array. No markdown fences."""


async def pantry_scan(image_base64: str | None = None, context: str = "counter") -> dict[str, Any]:
    if not image_base64:
        return {"error": "No image provided", "ingredients": []}

    llm = get_vision_llm()
    from langchain_core.messages import HumanMessage

    message = HumanMessage(content=[
        {"type": "text", "text": PROMPT.format(context=context)},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
    ])

    response = await llm.ainvoke([message])
    text = response.content.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        ingredients = json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Parse failed: {text[:200]}")
        ingredients = []

    validated = [i for i in ingredients if i.get("confidence", 0) >= 0.7]
    validated.sort(key=lambda x: x.get("confidence", 0), reverse=True)

    categories = {}
    for i in validated:
        cat = i.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "ingredients": validated,
        "total_detected": len(validated),
        "category_breakdown": categories,
        "freshness_alerts": [i["name"] for i in validated if i.get("freshness") in ("expire_soon", "spoiled")],
        "scan_context": context,
    }