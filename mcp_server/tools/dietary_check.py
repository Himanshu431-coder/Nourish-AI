"""Dietary compliance checker."""

from typing import Any

DIET_MAP = {
    "vegan": {"milk", "cheese", "cream", "butter", "yogurt", "egg", "eggs", "chicken", "beef", "pork", "bacon", "shrimp", "fish", "salmon", "tuna", "honey"},
    "vegetarian": {"chicken", "beef", "pork", "bacon", "shrimp", "fish", "salmon", "tuna", "crab", "lobster"},
    "gluten-free": {"wheat", "flour", "bread", "pasta", "barley", "rye", "soy sauce"},
    "keto": {"sugar", "rice", "potato", "bread", "pasta", "flour", "oats", "corn"},
    "dairy-free": {"milk", "cheese", "cream", "butter", "yogurt", "whey"},
}


async def dietary_check(items: list, allergies: list | None = None, diets: list | None = None) -> dict[str, Any]:
    items_lower = {i.lower() for i in items}
    violations = []
    if allergies:
        for allergy in allergies:
            for item in items_lower:
                if allergy.lower() in item:
                    violations.append({"item": item, "reason": f"Contains allergen: {allergy}", "severity": "critical"})
    if diets:
        for diet in diets:
            forbidden = DIET_MAP.get(diet.lower(), set())
            for item in items_lower:
                for f in forbidden:
                    if f in item:
                        violations.append({"item": item, "reason": f"Not {diet}: contains {f}", "severity": "warning"})
    return {
        "items_checked": len(items),
        "violations": violations,
        "is_safe": not any(v["severity"] == "critical" for v in violations),
        "warnings": [v for v in violations if v["severity"] == "warning"],
        "critical": [v for v in violations if v["severity"] == "critical"],
    }