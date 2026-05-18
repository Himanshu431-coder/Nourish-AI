"""Quick eval runner - 10 test cases, outputs grade."""

import asyncio
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import get_compiled_graph
from eval.dataset import EVAL_DATASET
from rag.retriever import seed_if_empty


async def run_eval():
    seed_if_empty()
    graph = get_compiled_graph()
    results = []

    for i, tc in enumerate(EVAL_DATASET):
        print(f"  [{i+1}/{len(EVAL_DATASET)}] {tc['name']}...", end=" ", flush=True)
        state = {
            "user_id": "eval", "image_base64": None, "text_input": tc.get("text_input", ""),
            "scan_context": "counter", "user_profile": tc.get("user_profile", {}),
            "detected_ingredients": [], "freshness_alerts": [], "recipe_candidates": [],
            "selected_recipe": None, "retry_count": 0, "max_retries": 1, "critic_feedback": "",
            "nutrition_assessment": None, "shopping_list": [], "voice_summary": "", "audio_path": None,
            "agent_steps": [], "tool_calls": [], "current_node": "", "input_safe": True,
            "guardrail_violations": [], "errors": [],
        }
        start = time.time()
        try:
            result = await graph.ainvoke(state)
            latency = time.time() - start
            nutrition = result.get("nutrition_assessment") or {}
            score = nutrition.get("score", 0)
            passes = nutrition.get("passes", False)

            if tc.get("category") == "guardrail":
                passed = not result.get("input_safe", True)
                print(f"{'✅ BLOCKED' if passed else '❌ NOT BLOCKED'} ({latency:.1f}s)")
            elif tc.get("category") == "allergy":
                has_conflict = bool(nutrition.get("allergen_conflicts"))
                print(f"{'✅ ALLERGEN FOUND' if has_conflict else '⚠️ MISSED'} ({latency:.1f}s)")
                passed = has_conflict
            else:
                passed = passes or score >= 0.5
                print(f"{'✅' if passed else '⚠️'} Score: {score:.0%} ({latency:.1f}s)")
            results.append({"name": tc["name"], "passed": passed, "score": score, "latency": round(latency, 1)})
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"name": tc["name"], "passed": False, "score": 0, "latency": 0, "error": str(e)})

    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    avg_latency = sum(r["latency"] for r in results) / len(results)
    grade = "A" if pass_rate >= 0.9 else "B" if pass_rate >= 0.8 else "C" if pass_rate >= 0.7 else "D"
    print(f"\n{'='*50}")
    print(f"  NOURISHAI Eval Report")
    print(f"{'='*50}")
    print(f"  Cases: {len(results)}")
    print(f"  Grade: {grade}")
    print(f"  Pass Rate: {pass_rate:.0%}")
    print(f"  Avg Latency: {avg_latency:.1f}s")
    print(f"{'='*50}")
    with open("eval_report.json", "w") as f:
        json.dump({"grade": grade, "pass_rate": pass_rate, "results": results}, f, indent=2)


if __name__ == "__main__":
    asyncio.run(run_eval())