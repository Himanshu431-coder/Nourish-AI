"""ChromaDB-based recipe retriever - local, zero config."""

import json
import os
import logging
from typing import Any

logger = logging.getLogger("nourishai.rag")

_chroma_client = None
_collection = None
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "recipes.jsonl")


def _get_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    import chromadb
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    _chroma_client = chromadb.PersistentClient(path=db_path)
    _collection = _chroma_client.get_or_create_collection(name="recipes", metadata={"hnsw:space": "cosine"})
    return _collection


def seed_if_empty():
    col = _get_collection()
    if col.count() > 0:
        return
    if not os.path.exists(DATA_PATH):
        _seed_defaults(col)
        return
    docs, metas, ids = [], [], []
    with open(DATA_PATH) as f:
        for i, line in enumerate(f):
            recipe = json.loads(line.strip())
            docs.append(f"{recipe['title']} | {', '.join(recipe.get('ingredients', []))} | {recipe.get('cuisine', '')} | {', '.join(recipe.get('dietary_tags', []))}")
            metas.append({"title": recipe["title"], "cuisine": recipe.get("cuisine", ""), "dietary_tags": json.dumps(recipe.get("dietary_tags", []))})
            ids.append(f"recipe_{i}")
    if docs:
        col.add(documents=docs, metadatas=metas, ids=ids)
        logger.info(f"Seeded {len(docs)} recipes into ChromaDB")


def _seed_defaults(col):
    defaults = [
        {"title": "High Protein Egg Frittata", "ingredients": ["eggs", "spinach", "feta cheese", "olive oil", "black pepper"], "cuisine": "mediterranean", "dietary_tags": ["high_protein", "gluten_free"]},
        {"title": "Chicken Stir Fry", "ingredients": ["chicken breast", "bell peppers", "broccoli", "soy sauce", "garlic", "ginger"], "cuisine": "asian", "dietary_tags": ["high_protein"]},
        {"title": "Greek Salad Bowl", "ingredients": ["cucumber", "tomatoes", "red onion", "feta cheese", "olives", "olive oil"], "cuisine": "mediterranean", "dietary_tags": ["vegetarian", "gluten_free"]},
        {"title": "Salmon with Roasted Vegetables", "ingredients": ["salmon fillet", "sweet potato", "asparagus", "lemon", "garlic", "olive oil"], "cuisine": "american", "dietary_tags": ["high_protein", "keto"]},
        {"title": "Black Bean Tacos", "ingredients": ["black beans", "corn tortillas", "avocado", "lime", "cilantro", "red onion"], "cuisine": "mexican", "dietary_tags": ["vegan", "gluten_free"]},
        {"title": "Turkey Meatballs", "ingredients": ["ground turkey", "breadcrumbs", "egg", "garlic", "parsley", "parmesan"], "cuisine": "italian", "dietary_tags": ["high_protein"]},
        {"title": "Quinoa Power Bowl", "ingredients": ["quinoa", "chickpeas", "cucumber", "cherry tomatoes", "tahini", "lemon"], "cuisine": "middle_eastern", "dietary_tags": ["vegan", "high_protein"]},
        {"title": "Beef and Broccoli", "ingredients": ["flank steak", "broccoli", "soy sauce", "garlic", "ginger", "sesame oil"], "cuisine": "asian", "dietary_tags": ["high_protein"]},
        {"title": "Caprese Salad", "ingredients": ["mozzarella", "tomatoes", "fresh basil", "olive oil", "balsamic vinegar"], "cuisine": "italian", "dietary_tags": ["vegetarian", "gluten_free", "keto"]},
        {"title": "Lentil Soup", "ingredients": ["red lentils", "onion", "carrots", "celery", "garlic", "cumin", "vegetable broth"], "cuisine": "middle_eastern", "dietary_tags": ["vegan", "high_protein"]},
        {"title": "Grilled Chicken Caesar Wrap", "ingredients": ["chicken breast", "romaine lettuce", "parmesan", "caesar dressing", "flour tortilla"], "cuisine": "american", "dietary_tags": ["high_protein"]},
        {"title": "Avocado Toast with Poached Egg", "ingredients": ["sourdough bread", "avocado", "egg", "red pepper flakes", "lemon juice"], "cuisine": "american", "dietary_tags": ["vegetarian"]},
        {"title": "Shrimp Scampi", "ingredients": ["shrimp", "linguine", "garlic", "butter", "white wine", "lemon", "parsley"], "cuisine": "italian", "dietary_tags": ["high_protein"]},
        {"title": "Vegetable Curry", "ingredients": ["cauliflower", "chickpeas", "coconut milk", "curry paste", "spinach", "rice"], "cuisine": "indian", "dietary_tags": ["vegan", "gluten_free"]},
        {"title": "Tuna Poke Bowl", "ingredients": ["sushi-grade tuna", "rice", "avocado", "edamame", "soy sauce", "sesame seeds"], "cuisine": "hawaiian", "dietary_tags": ["high_protein"]},
        {"title": "Mushroom Risotto", "ingredients": ["arborio rice", "mushrooms", "onion", "parmesan", "white wine", "vegetable broth"], "cuisine": "italian", "dietary_tags": ["vegetarian"]},
        {"title": "Baked Cod with Herbs", "ingredients": ["cod fillet", "lemon", "garlic", "parsley", "olive oil", "cherry tomatoes"], "cuisine": "mediterranean", "dietary_tags": ["high_protein", "gluten_free", "keto"]},
        {"title": "Peanut Butter Banana Smoothie", "ingredients": ["banana", "peanut butter", "milk", "protein powder", "ice"], "cuisine": "american", "dietary_tags": ["high_protein", "vegetarian"]},
        {"title": "Stuffed Bell Peppers", "ingredients": ["bell peppers", "ground beef", "rice", "tomato sauce", "onion", "cheese"], "cuisine": "american", "dietary_tags": ["high_protein"]},
        {"title": "Miso Glazed Tofu", "ingredients": ["firm tofu", "miso paste", "soy sauce", "mirin", "sesame oil", "green onions"], "cuisine": "asian", "dietary_tags": ["vegan", "high_protein"]},
    ]
    docs = [f"{r['title']} | {', '.join(r['ingredients'])} | {r['cuisine']} | {', '.join(r['dietary_tags'])}" for r in defaults]
    metas = [{"title": r["title"], "cuisine": r["cuisine"], "dietary_tags": json.dumps(r["dietary_tags"])} for r in defaults]
    ids = [f"recipe_{i}" for i in range(len(defaults))]
    col.add(documents=docs, metadatas=metas, ids=ids)
    logger.info(f"Seeded {len(defaults)} default recipes")


class RecipeRetriever:
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        col = _get_collection()
        if col.count() == 0:
            return []
        results = col.query(query_texts=[query], n_results=min(top_k, col.count()))
        recipes = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            recipes.append({
                "title": meta["title"],
                "cuisine": meta.get("cuisine", ""),
                "dietary_tags": json.loads(meta.get("dietary_tags", "[]")),
                "similarity": round(1 - dist, 3),
                "content": doc,
            })
        return recipes


_retriever = None

def get_retriever() -> RecipeRetriever:
    global _retriever
    if _retriever is None:
        seed_if_empty()
        _retriever = RecipeRetriever()
    return _retriever