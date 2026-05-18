"""Agent State Schema - flows through every LangGraph node."""

from __future__ import annotations
from typing import TypedDict, Annotated
from operator import add


class DetectedIngredient(TypedDict):
    name: str
    confidence: float
    quantity: str
    freshness: str
    category: str


class NutritionalAssessment(TypedDict):
    score: float
    grade: str
    passes: bool
    allergen_conflicts: list
    recommendation: str
    macros: dict


class RecipeCandidate(TypedDict):
    title: str
    ingredients: list
    instructions: list
    prep_time_min: int
    cook_time_min: int
    servings: int
    source: str


class NourishAIState(TypedDict):
    user_id: str
    image_base64: str | None
    text_input: str | None
    scan_context: str
    user_profile: dict
    detected_ingredients: list
    freshness_alerts: list
    recipe_candidates: list
    selected_recipe: dict | None
    retry_count: int
    max_retries: int
    critic_feedback: str
    nutrition_assessment: dict | None
    shopping_list: list
    voice_summary: str
    audio_path: str | None
    agent_steps: Annotated[list, add]
    tool_calls: Annotated[list, add]
    current_node: str
    input_safe: bool
    guardrail_violations: Annotated[list, add]
    errors: Annotated[list, add]