"""NOURISHAI MCP Server - Model Context Protocol with 6 tools."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from mcp_server.tools.pantry_scan import pantry_scan
from mcp_server.tools.recipe_search import recipe_search
from mcp_server.tools.nutrition_analyze import nutrition_analyze
from mcp_server.tools.shopping_list import shopping_list_manage
from mcp_server.tools.dietary_check import dietary_check
from mcp_server.tools.substitution import substitution_suggest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nourishai.mcp")

app = Server("nourishai-mcp")

TOOLS = {
    "pantry_scan": pantry_scan,
    "recipe_search": recipe_search,
    "nutrition_analyze": nutrition_analyze,
    "shopping_list_manage": shopping_list_manage,
    "dietary_check": dietary_check,
    "substitution_suggest": substitution_suggest,
}

TOOL_DEFS = [
    Tool(name="pantry_scan", description="Analyzes an image of ingredients. Returns detected items with confidence, quantity, freshness.", inputSchema={"type": "object", "properties": {"image_base64": {"type": "string"}, "context": {"type": "string", "default": "counter"}}}),
    Tool(name="recipe_search", description="Semantic search across recipe corpus. Filters by ingredients, diet, cuisine.", inputSchema={"type": "object", "properties": {"ingredients": {"type": "array", "items": {"type": "string"}}, "dietary_tags": {"type": "array", "items": {"type": "string"}}, "exclude_ingredients": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer", "default": 5}}, "required": ["ingredients"]}),
    Tool(name="nutrition_analyze", description="Analyzes recipe nutrition: macros, goal alignment score, allergen check.", inputSchema={"type": "object", "properties": {"recipe": {"type": "object"}, "health_goal": {"type": "string", "default": "general"}, "user_allergies": {"type": "array", "items": {"type": "string"}}}, "required": ["recipe"]}),
    Tool(name="shopping_list_manage", description="Create or read shopping lists.", inputSchema={"type": "object", "properties": {"action": {"type": "string", "enum": ["create", "read", "add_items"]}, "items": {"type": "array", "items": {"type": "object"}}}, "required": ["action"]}),
    Tool(name="dietary_check", description="Validates ingredients against dietary profile and allergens.", inputSchema={"type": "object", "properties": {"items": {"type": "array", "items": {"type": "string"}}, "allergies": {"type": "array", "items": {"type": "string"}}, "diets": {"type": "array", "items": {"type": "string"}}}, "required": ["items"]}),
    Tool(name="substitution_suggest", description="Suggests ingredient substitutions ranked by similarity.", inputSchema={"type": "object", "properties": {"ingredient": {"type": "string"}, "reason": {"type": "string", "enum": ["allergy", "unavailable", "nutrition"]}, "dietary_context": {"type": "array", "items": {"type": "string"}}}, "required": ["ingredient", "reason"]}),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOL_DEFS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info(f"MCP call: {name}")
    if name not in TOOLS:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        result = await TOOLS[name](**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        logger.error(f"Tool error [{name}]: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    logger.info("NOURISHAI MCP Server starting...")
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())