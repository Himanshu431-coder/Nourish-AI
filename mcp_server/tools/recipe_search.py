"""Recipe search using ChromaDB vector store."""

import logging
from typing import Any
from rag.retriever import get_retriever

logger = logging.getLogger("nourishai.recipe_search")


async def recipe_search(ingredients: list, dietary_tags: list | None = None, exclude_ingredients: list | None = None, cuisine: str | None = None, max_results: int = 5) -> list[dict[str, Any]]:
    retriever = get_retriever()
    query = ", ".join(ingredients)
    if dietary_tags:
        query += f" | dietary: {', '.join(dietary_tags)}"
    if cuisine:
        query += f" | cuisine: {cuisine}"
    results = retriever.search(query, top_k=max_results)
    if exclude_ingredients:
        exclude_lower = {e.lower() for e in exclude_ingredients}
        results = [r for r in results if not any(ex in r.get("content", "").lower() for ex in exclude_lower)]
    return results[:max_results]