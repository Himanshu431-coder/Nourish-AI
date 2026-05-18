"""Vision Node - detects ingredients via multimodal LLM."""

import logging
from datetime import datetime
from agents.state import NourishAIState
from mcp_server.tools.pantry_scan import pantry_scan

logger = logging.getLogger("nourishai.vision")


async def vision_node(state: NourishAIState) -> dict:
    step = {"node": "vision", "timestamp": datetime.utcnow().isoformat()}
    result = await pantry_scan(image_base64=state.get("image_base64"), context=state.get("scan_context", "counter"))
    ingredients = result.get("ingredients", [])
    alerts = result.get("freshness_alerts", [])
    step["ingredients_found"] = len(ingredients)
    step["tool_call"] = "pantry_scan"
    logger.info(f"[Vision] {len(ingredients)} ingredients: {[i['name'] for i in ingredients[:5]]}")
    return {
        "detected_ingredients": ingredients,
        "freshness_alerts": alerts,
        "current_node": "vision",
        "agent_steps": [step],
        "tool_calls": [{"tool": "pantry_scan", "count": len(ingredients), "timestamp": datetime.utcnow().isoformat()}],
    }