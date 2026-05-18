"""Nutrition analysis with health goal scoring."""

import json
import logging
from typing import Any
from core.llm import get_llm

logger = logging.getLogger("nourishai.nutrition")

GOAL_PROFILES = {
    "muscle_gain": {"protein_min": 25, "protein_max": 60, "carbs_min": 20, "carbs_max": 80, "fat_min": 10, "fat_max": 35, "cal_min": 400, "cal_max": 700},
    "weight_loss": {"protein_min": 20, "protein_max": 40, "carbs_min": 10, "carbs_max": 40, "fat_min": 8, "fat_max": 25, "cal_min": 200, "cal_max": 450},
    "heart_healthy": {"protein_min": 15, "protein_max": 40, "carbs_min": 20, "carbs_max": 60, "fat_min": 8, "fat_max": 20, "cal_min": 250, "cal_max": 550},
    "diabetic_friendly": {"protein_min": 15, "protein_max": 40, "carbs_min": 10, "carbs_max": 35, "fat_min": 10, "fat_max": 30, "cal_min": 200, "cal_max": 500},
    "general": {"protein_min": 10, "protein_max": 50, "carbs_min": 15, "carbs_max": 75, "fat_min": 5, "fat_max": 35, "cal_min": 150, "cal_max": 700},
}

ANALYSIS_PROMPT = """Analyze this recipe's nutrition per serving.
Recipe: {recipe_json}
Return JSON ONLY:
{{"macros": {{"protein_g": float, "carbs_g": float, "fat_g": float, "fiber_g": float, "sugar_g": float, "calories": int}}, "allergens_detected": ["str"], "glycemic_estimate": "low"|"medium"|"high"}}"""


def _score_macro(value, low, high):
    if low <= value <= high:
        return 1.0
    elif value < low:
        return max(0, value / low) if low > 0 else 0
    else:
        return max(0, 1 - (value - high) / high) if high > 0 else 0


async def nutrition_analyze(recipe: dict, health_goal: str = "general", user_allergies: list | None = None) -> dict[str, Any]:
    llm = get_llm(temperature=0.1)
    prompt = ANALYSIS_PROMPT.format(recipe_json=json.dumps(recipe))
    response = await llm.ainvoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        nutrition = json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Parse failed", "goal_score": {"overall_score": 0, "grade": "F", "individual_scores": {}, "target_ranges": {}}, "passes_goal": False, "allergen_conflicts": [], "is_safe": True, "recommendation": "Could not analyze nutrition.", "nutrition": {"macros": {}}}

    macros = nutrition.get("macros", {})
    goal = GOAL_PROFILES.get(health_goal, GOAL_PROFILES["general"])

    p = macros.get("protein_g", 0)
    c = macros.get("carbs_g", 0)
    f = macros.get("fat_g", 0)
    cal = macros.get("calories", 0)

    scores = {
        "protein": _score_macro(p, goal["protein_min"], goal["protein_max"]),
        "carbs": _score_macro(c, goal["carbs_min"], goal["carbs_max"]),
        "fat": _score_macro(f, goal["fat_min"], goal["fat_max"]),
        "calories": _score_macro(cal, goal["cal_min"], goal["cal_max"]),
    }

    overall = sum(scores.values()) / len(scores)
    grade = "A" if overall >= 0.9 else "B" if overall >= 0.75 else "C" if overall >= 0.6 else "D"

    detected_allergens = nutrition.get("allergens_detected", [])
    conflicts = [a for a in detected_allergens if any(ua.lower() in a.lower() for ua in (user_allergies or []))]

    return {
        "nutrition": nutrition,
        "goal_score": {
            "overall_score": round(overall, 3),
            "grade": grade,
            "individual_scores": scores,
            "target_ranges": {
                "protein": f"{goal['protein_min']}-{goal['protein_max']}g",
                "carbs": f"{goal['carbs_min']}-{goal['carbs_max']}g",
                "fat": f"{goal['fat_min']}-{goal['fat_max']}g",
                "calories": f"{goal['cal_min']}-{goal['cal_max']}kcal",
            },
        },
        "passes_goal": overall >= 0.7,
        "allergen_conflicts": conflicts,
        "is_safe": len(conflicts) == 0,
        "recommendation": _recommend(overall, conflicts, health_goal),
    }


def _recommend(score, conflicts, goal):
    if conflicts:
        return f"ALLERGEN ALERT: {', '.join(conflicts)}. NOT safe."
    if score >= 0.9:
        return f"Excellent fit for {goal} ({score:.0%})."
    if score >= 0.75:
        return f"Good fit for {goal} ({score:.0%}). Minor tweaks possible."
    if score >= 0.6:
        return f"Moderate fit for {goal} ({score:.0%}). Consider modifications."
    return f"Poor fit for {goal} ({score:.0%}). Recommend alternative."