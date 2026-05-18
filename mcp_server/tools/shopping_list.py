"""Shopping list management tool."""

import json
import os

SHOPPING_FILE = "shopping_list.json"


async def shopping_list_manage(action: str = "read", items: list | None = None) -> dict:
    if action == "read":
        if os.path.exists(SHOPPING_FILE):
            with open(SHOPPING_FILE) as f:
                return {"action": "read", "items": json.load(f)}
        return {"action": "read", "items": []}
    elif action == "create":
        data = items or []
        with open(SHOPPING_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return {"action": "created", "item_count": len(data), "items": data}
    elif action == "add_items":
        existing = []
        if os.path.exists(SHOPPING_FILE):
            with open(SHOPPING_FILE) as f:
                existing = json.load(f)
        new_items = items or []
        existing.extend(new_items)
        with open(SHOPPING_FILE, "w") as f:
            json.dump(existing, f, indent=2)
        return {"action": "updated", "item_count": len(existing), "items": existing}
    return {"error": f"Unknown action: {action}"}