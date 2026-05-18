"""Voice Node - generates text summary + TTS audio."""

import logging
import tempfile
from datetime import datetime
from agents.state import NourishAIState

logger = logging.getLogger("nourishai.voice")


async def voice_node(state: dict) -> dict:
    step = {"node": "voice", "timestamp": datetime.utcnow().isoformat()}
    recipe = state.get("selected_recipe", {})
    nutrition = state.get("nutrition_assessment", {})
    ingredients = state.get("detected_ingredients", [])
    profile = state.get("user_profile", {})

    title = recipe.get("title", "a meal")
    macros = nutrition.get("macros", {})
    protein = macros.get("protein_g", 0)
    calories = macros.get("calories", 0)
    grade = nutrition.get("grade", "?")
    goal = profile.get("health_goal", "general")

    detected = ", ".join([i["name"] for i in ingredients[:5]])
    alerts = state.get("freshness_alerts", [])

    summary_parts = [f"I've identified {detected}." if detected else "Based on your request,"]
    summary_parts.append(f"To support your {goal} goal, I suggest {title}")
    summary_parts.append(f"which provides {protein}g of protein and {calories} calories.")
    summary_parts.append(f"Nutrition grade: {grade}.")
    if alerts:
        summary_parts.append(f"Note: {', '.join(alerts)} may expire soon - use them first!")
    if nutrition.get("allergen_conflicts"):
        summary_parts.append(f"Allergen alert: {', '.join(nutrition['allergen_conflicts'])}.")

    summary = " ".join(summary_parts)

    audio_path = None
    try:
        from gtts import gTTS
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(text=summary, lang="en", slow=False)
        tts.save(tmp.name)
        audio_path = tmp.name
        step["audio"] = True
    except Exception as e:
        logger.warning(f"TTS failed: {e}")
        step["audio"] = False

    shopping = []
    try:
        available = {i["name"].lower() for i in ingredients}
        for ri in recipe.get("ingredients", []):
            if ri["name"].lower() not in available:
                shopping.append({"name": ri["name"], "amount": ri.get("amount", "1"), "purchased": False})
        step["shopping_items"] = len(shopping)
    except Exception:
        pass

    logger.info(f"[Voice] Summary: {summary[:80]}...")
    return {
        "voice_summary": summary,
        "audio_path": audio_path,
        "shopping_list": shopping,
        "current_node": "voice",
        "agent_steps": [step],
        "tool_calls": [{"tool": "voice_briefing", "audio": audio_path is not None, "timestamp": datetime.utcnow().isoformat()}],
    }