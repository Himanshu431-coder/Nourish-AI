"""Input Guardrail - blocks prompt injection and malicious inputs."""

import logging
from datetime import datetime

logger = logging.getLogger("nourishai.guard.input")

SUSPICIOUS = [
    "ignore previous", "forget your instructions", "you are now",
    "system prompt", "reveal your", "jailbreak", "DAN mode",
    "act as if", "pretend you are", "override", "bypass",
    "IGNORE ABOVE", "new instructions", "ignore all",
]


async def input_guard_node(state) -> dict:
    text = (state.get("text_input") or "") + " "
    combined = text.lower()
    for pattern in SUSPICIOUS:
        if pattern.lower() in combined:
            logger.warning(f"[InputGuard] Blocked: '{pattern}'")
            return {
                "input_safe": False,
                "current_node": "input_guard",
                "guardrail_violations": [f"Blocked pattern: {pattern}"],
                "agent_steps": [{"node": "input_guard", "result": "BLOCKED", "reason": pattern, "timestamp": datetime.utcnow().isoformat()}],
            }
    return {
        "input_safe": True,
        "current_node": "input_guard",
        "agent_steps": [{"node": "input_guard", "result": "SAFE", "timestamp": datetime.utcnow().isoformat()}],
    }