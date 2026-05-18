"""LangGraph Orchestration - conditional routing + self-correction loop."""

import logging
from langgraph.graph import StateGraph, END, START
from agents.state import NourishAIState
from agents.nodes.vision import vision_node
from agents.nodes.recipe import recipe_node
from agents.nodes.critic import critic_node
from agents.nodes.voice import voice_node
from guardrails.input_guard import input_guard_node

logger = logging.getLogger("nourishai.graph")


def route_after_guard(state):
    if not state.get("input_safe", True):
        return END
    if state.get("image_base64"):
        return "vision"
    return "recipe"


def route_after_vision(state):
    if state.get("detected_ingredients"):
        return "recipe"
    return END


def route_after_critic(state):
    assessment = state.get("nutrition_assessment")
    if not assessment:
        return "recipe"

    # If allergen found, go straight to voice (no retry - allergen detection IS the result)
    if not assessment.get("is_safe", True):
        logger.info("Allergen detected - skipping retry, going to voice")
        return "voice"

    # If passes, go to voice
    if assessment["passes"]:
        return "voice"

    # Otherwise retry up to max
    retry = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    if retry >= max_retries:
        logger.warning("Max retries reached, proceeding with best candidate")
        return "voice"

    logger.info(f"Critic rejected (score={assessment['score']}). Retry {retry}/{max_retries}")
    return "recipe"


def build_graph():
    graph = StateGraph(NourishAIState)
    graph.add_node("input_guard", input_guard_node)
    graph.add_node("vision", vision_node)
    graph.add_node("recipe", recipe_node)
    graph.add_node("critic", critic_node)
    graph.add_node("voice", voice_node)
    graph.add_edge(START, "input_guard")
    graph.add_conditional_edges("input_guard", route_after_guard, {"vision": "vision", "recipe": "recipe", END: END})
    graph.add_conditional_edges("vision", route_after_vision, {"recipe": "recipe", END: END})
    graph.add_edge("recipe", "critic")
    graph.add_conditional_edges("critic", route_after_critic, {"recipe": "recipe", "voice": "voice"})
    graph.add_edge("voice", END)
    return graph


def get_compiled_graph():
    return build_graph().compile()