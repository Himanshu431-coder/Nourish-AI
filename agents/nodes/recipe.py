"""Recipe Node - generates recipe from ingredients using RAG + LLM."""

import json
import logging
from datetime import datetime
from agents.state import NourishAIState
from mcp_server.tools.recipe_search import recipe_search
from core.llm import get_llm

logger = logging.getLogger("nourishai.recipe")

RECIPE_PROMPT = """You are a world-class chef. Create a recipe using these ingredients:
Available: {ingredients}
User goal: {goal}
Allergies: {allergies}
Critic feedback (if retry): {feedback}
Return JSON ONLY:
{{"title": "string", "ingredients": [{{"name": "str", "amount": "str", "unit": "str"}}], "instructions": ["step1", "step2"], "prep_time_min": int, "cook_time_min": int, "servings": int, "cuisine": "string", "dietary_tags": ["string"]}}
Rules: Use as many available ingredients as possible. STRICTLY AVOID: {allergies}. Optimize for: {goal}. If critic feedback exists, ADDRESS IT directly. No markdown fences, just JSON."""


async def recipe_node(state: NourishAIState) -> dict:
    step = {"node": "recipe", "timestamp": datetime.utcnow().isoformat()}
    ingredients = state.get("detected_ingredients", [])
    ingredient_names = [i["name"] for i in ingredients] if ingredients else []
    text_input = state.get("text_input", "")
    profile = state.get("user_profile", {})
    goal = profile.get("health_goal", "general")
    allergies = profile.get("allergies", [])
    feedback = state.get("critic_feedback", "None")

    rag_results = []
    if ingredient_names:
        try:
            rag_results = await recipe_search(ingredients=ingredient_names, dietary_tags=[goal] if goal != "general" else [], exclude_ingredients=allergies, max_results=3)
            step["rag_results"] = len(rag_results)
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")

    llm = get_llm()
    prompt = RECIPE_PROMPT.format(
        ingredients=", ".join(ingredient_names) if ingredient_names else text_input,
        goal=goal, allergies=", ".join(allergies) if allergies else "none", feedback=feedback,
    )
    response = await llm.ainvoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        recipe = json.loads(text)
        recipe["source"] = "generated"
    except json.JSONDecodeError:
        logger.error(f"Failed to parse recipe: {text[:200]}")
        recipe = {"title": "Custom Recipe", "ingredients": [{"name": n, "amount": "1", "unit": "piece"} for n in ingredient_names[:5]], "instructions": ["Combine all ingredients and cook until done."], "prep_time_min": 10, "cook_time_min": 20, "servings": 2, "source": "fallback"}

    step["recipe"] = recipe["title"]
    logger.info(f"[Recipe] Generated: {recipe['title']}")
    return {
        "selected_recipe": recipe,
        "recipe_candidates": [recipe],
        "current_node": "recipe",
        "agent_steps": [step],
        "tool_calls": [{"tool": "recipe_search", "results": len(rag_results), "timestamp": datetime.utcnow().isoformat()}],
    }