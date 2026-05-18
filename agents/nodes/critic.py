"""Critic Node - self-correction loop. Scores nutrition, rejects bad recipes."""

import logging
from datetime import datetime
from agents.state import NourishAIState
from mcp_server.tools.nutrition_analyze import nutrition_analyze

logger = logging.getLogger("nourishai.critic")


async def critic_node(state: NourishAIState) -> dict:
    step = {"node": "critic", "timestamp": datetime.utcnow().isoformat()}
    recipe = state.get("selected_recipe")
    if not recipe:
        return {
            "nutrition_assessment": {"score": 0.0, "grade": "F", "passes": False, "allergen_conflicts": [], "recommendation": "No recipe", "macros": {}, "is_safe": True},
            "critic_feedback": "No recipe to evaluate.",
            "current_node": "critic",
            "agent_steps": [step],
        }

    profile = state.get("user_profile", {})
    goal = profile.get("health_goal", "general")
    allergies = profile.get("allergies", [])

    result = await nutrition_analyze(recipe=recipe, health_goal=goal, user_allergies=allergies)
    gs = result.get("goal_score", {})
    assessment = {
        "score": gs.get("overall_score", 0),
        "grade": gs.get("grade", "F"),
        "passes": result.get("passes_goal", False),
        "allergen_conflicts": result.get("allergen_conflicts", []),
        "recommendation": result.get("recommendation", ""),
        "macros": result.get("nutrition", {}).get("macros", {}),
        "is_safe": result.get("is_safe", True),
    }

    # Also check input text/ingredients for allergens
    text_input = (state.get("text_input") or "").lower()
    detected = state.get("detected_ingredients", [])
    detected_names = [i.get("name", "").lower() for i in detected]

    for allergy in allergies:
        allergy_lower = allergy.lower()
        # Check text input
        if allergy_lower in text_input:
            conflict = f"Input contains allergen: {allergy}"
            if conflict not in assessment["allergen_conflicts"]:
                assessment["allergen_conflicts"].append(conflict)
                assessment["is_safe"] = False
        # Check detected ingredients
        for name in detected_names:
            if allergy_lower in name:
                conflict = f"Detected allergen: {allergy} ({name})"
                if conflict not in assessment["allergen_conflicts"]:
                    assessment["allergen_conflicts"].append(conflict)
                    assessment["is_safe"] = False
        # Check recipe ingredients
        for ri in recipe.get("ingredients", []):
            ri_name = ri.get("name", "").lower()
            if allergy_lower in ri_name:
                conflict = f"Recipe contains allergen: {allergy} ({ri_name})"
                if conflict not in assessment["allergen_conflicts"]:
                    assessment["allergen_conflicts"].append(conflict)
                    assessment["is_safe"] = False

    retry = state.get("retry_count", 0)
    if not assessment["passes"]:
        parts = []
        if assessment["allergen_conflicts"]:
            parts.append(f"ALLERGEN CONFLICT: {', '.join(assessment['allergen_conflicts'])}. Substitute these.")
        low = {k: v for k, v in gs.get("individual_scores", {}).items() if v < 0.6}
        if low:
            parts.append(f"Low scores: {low}. Adjust to fit: {gs.get('target_ranges', {})}")
        feedback = " | ".join(parts) if parts else "Does not meet goal. Try different ratios."
    else:
        feedback = "Passes all checks."

    step["score"] = assessment["score"]
    step["grade"] = assessment["grade"]
    step["passes"] = assessment["passes"]
    step["retry"] = retry
    logger.info(f"[Critic] {assessment['score']:.0%} ({assessment['grade']}) pass={assessment['passes']} retry={retry}")

    return {
        "nutrition_assessment": assessment,
        "critic_feedback": feedback,
        "retry_count": retry + 1 if not assessment["passes"] else retry,
        "current_node": "critic",
        "agent_steps": [step],
        "tool_calls": [{"tool": "nutrition_analyze", "score": assessment["score"], "timestamp": datetime.utcnow().isoformat()}],
    }