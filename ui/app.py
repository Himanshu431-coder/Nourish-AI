"""NOURISHAI - Premium Streamlit UI with animations and live agent streaming."""

import asyncio
import base64
import json
import time
import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import get_compiled_graph
from db.database import init_db
from rag.retriever import seed_if_empty

st.set_page_config(page_title="Nourish AI", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

# ── PREMIUM CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

* { box-sizing: border-box; }

.stApp {
    font-family: 'Inter', sans-serif;
    background: #050505;
    color: #fafafa;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* Sidebar */
.stSidebar {
    background: linear-gradient(180deg, #0a0a0a 0%, #0f0f0f 100%);
    border-right: 1px solid #1a1a1a;
}
.stSidebar .stMarkdown { color: #a0a0a0; }

/* Brand */
.brand-container {
    padding: 24px 0 16px;
    text-align: center;
}
.brand-logo {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, #f97316 0%, #ef4444 50%, #ec4899 100%);
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px;
    margin: 0 auto 12px;
    box-shadow: 0 8px 32px rgba(249, 115, 22, 0.3);
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}
.brand-name {
    font-size: 26px;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #f97316, #ef4444, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.brand-sub {
    font-size: 11px;
    color: #444;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}
.brand-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #333, transparent);
    margin: 16px 0;
}

/* Developer Credit */
.dev-credit {
    text-align: center;
    padding: 16px 0;
    margin-top: auto;
}
.dev-credit .label {
    font-size: 10px;
    color: #333;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 4px;
}
.dev-credit .name {
    font-size: 13px;
    color: #666;
    font-weight: 600;
}
.dev-credit .name span {
    background: linear-gradient(135deg, #f97316, #ef4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Section Headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.section-header .icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.section-header .icon.orange { background: #f9731620; }
.section-header .icon.green { background: #22c55e20; }
.section-header .icon.blue { background: #3b82f620; }
.section-header .icon.red { background: #ef444420; }
.section-header .icon.purple { background: #a855f720; }
.section-header .text h3 {
    font-size: 16px; font-weight: 700; color: #fafafa; margin: 0;
}
.section-header .text p {
    font-size: 11px; color: #555; margin: 0;
}

/* Cards */
.card {
    background: #0f0f0f;
    border: 1px solid #1a1a1a;
    border-radius: 14px;
    padding: 20px;
    margin: 12px 0;
    transition: all 0.3s ease;
}
.card:hover {
    border-color: #2a2a2a;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.card-pass {
    border-color: #22c55e30;
    background: linear-gradient(135deg, #0a0f0a, #0f0f0f);
}
.card-fail {
    border-color: #f59e0b30;
    background: linear-gradient(135deg, #0f0d0a, #0f0f0f);
}
.card-error {
    border-color: #ef444430;
    background: linear-gradient(135deg, #0f0a0a, #0f0f0f);
}

/* Ingredient Chips */
.ing-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.ing-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: #141414;
    border: 1px solid #222;
    border-radius: 24px;
    font-size: 13px;
    color: #e0e0e0;
    transition: all 0.2s ease;
    animation: fadeInUp 0.3s ease forwards;
    opacity: 0;
}
.ing-chip:hover { border-color: #444; transform: translateY(-1px); }
.ing-chip .conf {
    font-size: 10px;
    color: #555;
    font-family: 'JetBrains Mono', monospace;
}
.ing-chip.alert {
    border-color: #f59e0b40;
    color: #f59e0b;
    background: #1a1508;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Macro Grid */
.macro-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
.macro-item {
    text-align: center;
    padding: 14px 8px;
    background: #0a0a0a;
    border-radius: 10px;
    border: 1px solid #1a1a1a;
    transition: all 0.3s ease;
}
.macro-item:hover {
    border-color: #333;
    transform: translateY(-2px);
}
.macro-value {
    font-size: 22px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #fafafa, #ccc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.macro-label {
    font-size: 10px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Score Badge */
.score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px; height: 56px;
    border-radius: 14px;
    font-size: 28px;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
    animation: scorePop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
@keyframes scorePop {
    0% { transform: scale(0); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
.score-A { background: #22c55e18; color: #22c55e; border: 2px solid #22c55e40; }
.score-B { background: #3b82f618; color: #3b82f6; border: 2px solid #3b82f640; }
.score-C { background: #f59e0b18; color: #f59e0b; border: 2px solid #f59e0b40; }
.score-D { background: #ef444418; color: #ef4444; border: 2px solid #ef444440; }

/* Tool Badge */
.tool-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background: #141414;
    border: 1px solid #222;
    border-radius: 8px;
    font-size: 11px;
    color: #f97316;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin: 3px;
    transition: all 0.2s ease;
}
.tool-badge:hover { border-color: #f97316; }

/* Timeline */
.timeline-item {
    display: flex;
    gap: 14px;
    padding: 10px 0;
    border-left: 2px solid #1a1a1a;
    padding-left: 20px;
    margin-left: 8px;
    transition: all 0.3s ease;
    animation: slideIn 0.4s ease forwards;
    opacity: 0;
}
.timeline-item.active { border-left-color: #f97316; }
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}
.timeline-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    background: #333;
    margin-top: 4px;
    flex-shrink: 0;
    transition: all 0.3s ease;
}
.timeline-dot.success { background: #22c55e; box-shadow: 0 0 8px #22c55e40; }
.timeline-dot.warning { background: #f59e0b; box-shadow: 0 0 8px #f59e0b40; }
.timeline-dot.error { background: #ef4444; box-shadow: 0 0 8px #ef444440; }
.node-label {
    font-weight: 700; font-size: 13px; color: #fafafa;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.node-detail {
    font-size: 12px; color: #666; margin-top: 3px;
    font-family: 'JetBrains Mono', monospace;
}

/* Shopping List */
.shop-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    font-size: 13px;
    border-bottom: 1px solid #1a1a1a;
    animation: fadeInUp 0.3s ease forwards;
    opacity: 0;
}
.shop-item:last-child { border-bottom: none; }
.shop-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f97316, #ef4444);
    flex-shrink: 0;
}

/* Recipe Instructions */
.recipe-step {
    display: flex;
    gap: 12px;
    padding: 8px 0;
    animation: fadeInUp 0.3s ease forwards;
    opacity: 0;
}
.step-num {
    width: 28px; height: 28px;
    border-radius: 8px;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #f97316;
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
}
.step-text {
    font-size: 14px;
    color: #ccc;
    line-height: 1.6;
    padding-top: 3px;
}

/* Ingredient List */
.ing-list-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 13px;
    color: #bbb;
    animation: fadeInUp 0.2s ease forwards;
    opacity: 0;
}
.ing-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #f97316;
    flex-shrink: 0;
}

/* Stat Card */
.stat-card {
    text-align: center;
    padding: 20px;
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 12px;
    transition: all 0.3s ease;
}
.stat-card:hover {
    border-color: #333;
    transform: translateY(-2px);
}
.stat-value {
    font-size: 32px;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #f97316, #ef4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Export Button */
.export-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    color: #888;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.export-btn:hover {
    border-color: #f97316;
    color: #f97316;
}

/* Latency Badge */
.latency-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 20px;
    font-size: 11px;
    color: #555;
    font-family: 'JetBrains Mono', monospace;
}
.latency-badge .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Guard Blocked */
.blocked-msg {
    text-align: center;
    padding: 40px 20px;
    animation: shake 0.5s ease;
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
.blocked-icon {
    font-size: 48px;
    margin-bottom: 12px;
}
.blocked-text {
    font-size: 16px;
    font-weight: 700;
    color: #ef4444;
}
.blocked-detail {
    font-size: 12px;
    color: #555;
    margin-top: 8px;
}

/* Hide Streamlit defaults */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar selectbox */
.stSidebar .stSelectbox label, .stSidebar .stMultiselect label { display: none; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0a0a0a;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #1a1a1a;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #666;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: #141414 !important;
    color: #f97316 !important;
    border: 1px solid #2a2a2a;
}
</style>
""", unsafe_allow_html=True)


# ── INIT ─────────────────────────────────────────────────────────────
@st.cache_resource
def init_system():
    init_db()
    seed_if_empty()
    return get_compiled_graph()


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


compiled_graph = init_system()

# Session state for history
if "history" not in st.session_state:
    st.session_state["history"] = []


# ── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-logo">🍳</div>
        <h1 class="brand-name">Nourish AI</h1>
        <p class="brand-sub">Culinary Intelligence</p>
    </div>
    <div class="brand-divider"></div>
    """, unsafe_allow_html=True)

    st.markdown("**🎯 Health Goal**")
    health_goal = st.selectbox("Goal", ["muscle_gain", "weight_loss", "heart_healthy", "diabetic_friendly", "general"], index=0, label_visibility="collapsed")

    st.markdown("**⚠️ Allergies**")
    allergies = st.multiselect("Allergens", ["peanuts", "tree nuts", "milk", "eggs", "wheat", "soy", "fish", "shellfish"], default=[], label_visibility="collapsed")

    st.markdown("**🥗 Diet**")
    diets = st.multiselect("Dietary Tags", ["vegan", "vegetarian", "gluten-free", "keto", "dairy-free", "high_protein"], default=[], label_visibility="collapsed")

    st.markdown("""
    <div class="brand-divider"></div>
    <div style="font-size:12px;color:#333;line-height:1.8;">
        <span style="color:#f97316;">&#9679;</span> MCP Tools: <b>6</b><br>
        <span style="color:#22c55e;">&#9679;</span> Agent Nodes: <b>5</b><br>
        <span style="color:#3b82f6;">&#9679;</span> Guardrails: <b>2</b><br>
        <span style="color:#a855f7;">&#9679;</span> RAG: <b>ChromaDB</b><br>
        <span style="color:#ef4444;">&#9679;</span> LLM: <b>Groq + Gemini</b>
    </div>
    <div class="brand-divider"></div>
    <div class="dev-credit">
        <div class="label">Built by</div>
        <div class="name"><span>Himanshu Tapde</span></div>
    </div>
    """, unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────────────
def make_state(image_b64=None, text=None, ctx="counter"):
    return {
        "user_id": "demo_user", "image_base64": image_b64, "text_input": text,
        "scan_context": ctx, "user_profile": {"health_goal": health_goal, "allergies": allergies, "diets": diets},
        "detected_ingredients": [], "freshness_alerts": [], "recipe_candidates": [],
        "selected_recipe": None, "retry_count": 0, "max_retries": 3, "critic_feedback": "",
        "nutrition_assessment": None, "shopping_list": [], "voice_summary": "", "audio_path": None,
        "agent_steps": [], "tool_calls": [], "current_node": "", "input_safe": True,
        "guardrail_violations": [], "errors": [],
    }


def export_recipe(recipe, nutrition, voice_summary):
    lines = [
        f"{'='*50}",
        f"  Nourish AI - Recipe Export",
        f"{'='*50}",
        f"",
        f"  {recipe.get('title', 'Recipe')}",
        f"",
        f"  Prep: {recipe.get('prep_time_min', '?')} min | Cook: {recipe.get('cook_time_min', '?')} min | Servings: {recipe.get('servings', '?')}",
        f"",
        f"  Ingredients:",
    ]
    for ing in recipe.get("ingredients", []):
        lines.append(f"    - {ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}")
    lines.append("")
    lines.append("  Instructions:")
    for i, step in enumerate(recipe.get("instructions", []), 1):
        lines.append(f"    {i}. {step}")
    if nutrition:
        macros = nutrition.get("macros", {})
        lines.append("")
        lines.append(f"  Nutrition: {nutrition.get('grade', '?')} ({nutrition.get('score', 0):.0%})")
        lines.append(f"    Protein: {macros.get('protein_g', 0):.0f}g | Carbs: {macros.get('carbs_g', 0):.0f}g | Fat: {macros.get('fat_g', 0):.0f}g | Calories: {macros.get('calories', 0)}")
        lines.append(f"    {nutrition.get('recommendation', '')}")
    if voice_summary:
        lines.append("")
        lines.append(f"  Summary: {voice_summary}")
    lines.append("")
    lines.append(f"{'='*50}")
    lines.append(f"  Generated by Nourish AI | Built by Himanshu Tapde")
    lines.append(f"{'='*50}")
    return "\n".join(lines)


def render_results(result):
    # Check if blocked
    if not result.get("input_safe", True):
        violations = result.get("guardrail_violations", [])
        st.markdown("""
        <div class="blocked-msg">
            <div class="blocked-icon">🛡️</div>
            <div class="blocked-text">Input Blocked</div>
            <div class="blocked-detail">Malicious input detected. Request rejected by guardrail.</div>
            <div class="blocked-detail" style="color:#ef4444; margin-top:12px;">""" + (violations[0] if violations else "") + """</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Ingredients
    ingredients = result.get("detected_ingredients", [])
    if ingredients:
        st.markdown("""
        <div class="section-header">
            <div class="icon orange">👁️</div>
            <div class="text"><h3>Detected Ingredients</h3><p>""" + str(len(ingredients)) + """ items found</p></div>
        </div>
        """, unsafe_allow_html=True)
        chips = ""
        for idx, ing in enumerate(ingredients):
            conf = ing.get("confidence", 0)
            is_alert = ing.get("freshness") in ("expire_soon", "spoiled")
            css = "alert" if is_alert else ""
            chips += f'<div class="ing-chip" style="animation-delay:{idx * 0.05}s">{ing["name"]}<span class="conf">{conf:.0%}</span></div>'
        st.markdown(f'<div class="ing-grid">{chips}</div>', unsafe_allow_html=True)
        alerts = result.get("freshness_alerts", [])
        if alerts:
            st.markdown(f'<div style="color:#f59e0b;font-size:12px;margin-top:8px;">⏰ Expiring soon: {", ".join(alerts)}</div>', unsafe_allow_html=True)

    # Recipe
    recipe = result.get("selected_recipe")
    if recipe:
        st.markdown(f"""
        <div class="section-header">
            <div class="icon green">🍳</div>
            <div class="text"><h3>{recipe.get('title', 'Recipe')}</h3><p>Generated recipe</p></div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="stat-card"><div class="stat-value" style="font-size:20px;">' + str(recipe.get('prep_time_min', '?')) + '</div><div class="stat-label">Prep min</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="stat-card"><div class="stat-value" style="font-size:20px;">' + str(recipe.get('cook_time_min', '?')) + '</div><div class="stat-label">Cook min</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="stat-card"><div class="stat-value" style="font-size:20px;">' + str(recipe.get('servings', '?')) + '</div><div class="stat-label">Servings</div></div>', unsafe_allow_html=True)

        st.markdown("**Ingredients**")
        for idx, ing in enumerate(recipe.get("ingredients", [])):
            st.markdown(f'<div class="ing-list-item" style="animation-delay:{idx * 0.03}s"><div class="ing-dot"></div>{ing.get("amount", "")} {ing.get("unit", "")} {ing.get("name", "")}</div>', unsafe_allow_html=True)

        st.markdown("**Instructions**")
        for idx, step in enumerate(recipe.get("instructions", []), 1):
            st.markdown(f'<div class="recipe-step" style="animation-delay:{idx * 0.05}s"><div class="step-num">{idx}</div><div class="step-text">{step}</div></div>', unsafe_allow_html=True)

    # Nutrition
    nutrition = result.get("nutrition_assessment")
    if nutrition:
        score = nutrition.get("score", 0)
        grade = nutrition.get("grade", "?")
        passes = nutrition.get("passes", False)
        macros = nutrition.get("macros", {})
        cc = "card-pass" if passes else "card-fail"

        st.markdown(f"""
        <div class="card {cc}">
            <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;">
                <div class="score-badge score-{grade}">{grade}</div>
                <div>
                    <div style="font-size:18px;font-weight:800;">Nutrition Assessment</div>
                    <div style="font-size:12px;color:#666;margin-top:2px;">Score: {score:.0%} - {'PASS ✅' if passes else 'NEEDS WORK ⚠️'}</div>
                </div>
            </div>
            <div class="macro-grid">
                <div class="macro-item"><div class="macro-value">{macros.get('protein_g', 0):.0f}g</div><div class="macro-label">Protein</div></div>
                <div class="macro-item"><div class="macro-value">{macros.get('carbs_g', 0):.0f}g</div><div class="macro-label">Carbs</div></div>
                <div class="macro-item"><div class="macro-value">{macros.get('fat_g', 0):.0f}g</div><div class="macro-label">Fat</div></div>
                <div class="macro-item"><div class="macro-value">{macros.get('calories', 0)}</div><div class="macro-label">Calories</div></div>
            </div>
            <div style="margin-top:16px;font-size:13px;color:#777;padding-top:12px;border-top:1px solid #1a1a1a;">{nutrition.get('recommendation', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        if nutrition.get("allergen_conflicts"):
            st.markdown(f'<div style="color:#ef4444;font-size:13px;padding:8px 12px;background:#ef444410;border:1px solid #ef444430;border-radius:8px;">🚨 ALLERGEN CONFLICT: {", ".join(nutrition["allergen_conflicts"])}</div>', unsafe_allow_html=True)

    # Voice Summary
    voice_summary = result.get("voice_summary", "")
    if voice_summary:
        st.markdown("""
        <div class="section-header">
            <div class="icon purple">🗣️</div>
            <div class="text"><h3>Voice Briefing</h3><p>Audio summary</p></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div style="color:#aaa;font-size:14px;line-height:1.7;padding:8px 0;">{voice_summary}</div>', unsafe_allow_html=True)
        audio_path = result.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

    # Shopping List
    shopping = result.get("shopping_list", [])
    if shopping:
        st.markdown("""
        <div class="section-header">
            <div class="icon blue">🛒</div>
            <div class="text"><h3>Shopping List</h3><p>""" + str(len(shopping)) + """ missing items</p></div>
        </div>
        """, unsafe_allow_html=True)
        shop_html = ""
        for idx, item in enumerate(shopping):
            shop_html += f'<div class="shop-item" style="animation-delay:{idx * 0.05}s"><div class="shop-dot"></div>{item.get("name", "?")} <span style="color:#555;font-size:12px;">({item.get("amount", "")})</span></div>'
        st.markdown(shop_html, unsafe_allow_html=True)

    # Footer: Latency + Export
    footer_parts = []
    if "last_latency" in st.session_state:
        footer_parts.append(f'<div class="latency-badge"><div class="dot"></div>{st.session_state["last_latency"]:.1f}s</div>')
    if recipe:
        export_text = export_recipe(recipe, nutrition, voice_summary)
        b64 = base64.b64encode(export_text.encode()).decode()
        footer_parts.append(f'<a class="export-btn" href="data:text/plain;base64,{b64}" download="nourishai_recipe.txt">📥 Export Recipe</a>')
    if footer_parts:
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-top:16px;">{" ".join(footer_parts)}</div>', unsafe_allow_html=True)


# ── TABS ─────────────────────────────────────────────────────────────
tab_scan, tab_text, tab_trace, tab_dashboard, tab_history = st.tabs([
    "📷  Scan", "💬  Text", "🤖  Agent Trace", "📊  Dashboard", "📋  History"
])

# ── Scan Tab ─────────────────────────────────────────────────────────
with tab_scan:
    st.markdown("""
    <div class="section-header">
        <div class="icon orange">📷</div>
        <div class="text"><h3>Scan Your Ingredients</h3><p>Take a photo or upload an image</p></div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.camera_input("📷 Take a photo", label_visibility="collapsed")
        if not uploaded_file:
            uploaded_file = st.file_uploader("Or upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    with col2:
        scan_context = st.radio("Location", ["counter", "fridge", "pantry"], horizontal=True)
        run_scan = st.button("🚀 Run Agent", type="primary", use_container_width=True)

    if uploaded_file and run_scan:
        image_b64 = base64.b64encode(uploaded_file.read()).decode()
        with st.spinner("🤖 Agent thinking..."):
            start_time = time.time()
            result = run_async(compiled_graph.ainvoke(make_state(image_b64=image_b64, ctx=scan_context)))
            elapsed = time.time() - start_time
        st.session_state["last_result"] = result
        st.session_state["last_latency"] = elapsed
        st.session_state["history"].append({"time": datetime.utcnow().isoformat(), "type": "scan", "latency": round(elapsed, 1), "score": result.get("nutrition_assessment", {}).get("score", 0), "grade": result.get("nutrition_assessment", {}).get("grade", "?")})
        st.success(f"✅ Done in {elapsed:.1f}s")
        render_results(result)

# ── Text Tab ─────────────────────────────────────────────────────────
with tab_text:
    st.markdown("""
    <div class="section-header">
        <div class="icon green">💬</div>
        <div class="text"><h3>Describe What You Have</h3><p>Tell me your ingredients and goals</p></div>
    </div>
    """, unsafe_allow_html=True)
    text_input = st.text_area("What ingredients do you have?", placeholder="I have chicken, broccoli, and rice. I want something high protein...", height=100, label_visibility="collapsed")
    if st.button("🚀 Generate Recipe", type="primary", use_container_width=True) and text_input:
        with st.spinner("🤖 Agent thinking..."):
            start_time = time.time()
            result = run_async(compiled_graph.ainvoke(make_state(text=text_input)))
            elapsed = time.time() - start_time
        st.session_state["last_result"] = result
        st.session_state["last_latency"] = elapsed
        st.session_state["history"].append({"time": datetime.utcnow().isoformat(), "type": "text", "latency": round(elapsed, 1), "score": result.get("nutrition_assessment", {}).get("score", 0), "grade": result.get("nutrition_assessment", {}).get("grade", "?")})
        st.success(f"✅ Done in {elapsed:.1f}s")
        render_results(result)

# ── Agent Trace Tab ──────────────────────────────────────────────────
with tab_trace:
    st.markdown("""
    <div class="section-header">
        <div class="icon purple">🤖</div>
        <div class="text"><h3>Agent Execution Trace</h3><p>Step-by-step agent pipeline</p></div>
    </div>
    """, unsafe_allow_html=True)
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        steps = result.get("agent_steps", [])
        tools = result.get("tool_calls", [])
        icons = {"input_guard": "🛡️", "vision": "👁️", "recipe": "👨‍🍳", "critic": "⚖️", "voice": "🗣️"}
        timeline_html = ""
        for idx, step in enumerate(steps):
            node = step.get("node", "?")
            icon = icons.get(node, "⚙️")
            is_ok = step.get("passes", step.get("ingredients_found", 0) > 0 or step.get("audio", False))
            dot = "success" if is_ok else ("warning" if step.get("result") == "BLOCKED" else "success")
            detail = ""
            if "ingredients_found" in step: detail = f"{step['ingredients_found']} ingredients detected"
            elif "score" in step: detail = f"Score: {step['score']:.0%} ({step['grade']}) - {'PASS' if step.get('passes') else 'RETRY'}"
            elif "recipe" in step: detail = f"Generated: {step['recipe']}"
            elif "audio" in step: detail = f"Audio: {'✅' if step['audio'] else '❌'}"
            elif step.get("result") == "BLOCKED": detail = f"BLOCKED: {step.get('reason', '')}"
            elif step.get("result") == "SAFE": detail = "Input verified safe"
            timeline_html += f'<div class="timeline-item active" style="animation-delay:{idx * 0.1}s"><div class="timeline-dot {dot}"></div><div><div class="node-label">{icon} {node.replace("_", " ").title()}</div><div class="node-detail">{detail}</div></div></div>'
        st.markdown(timeline_html, unsafe_allow_html=True)
        if tools:
            st.markdown("""
            <div class="section-header" style="margin-top:24px;">
                <div class="icon red">🔧</div>
                <div class="text"><h3>MCP Tool Calls</h3><p>Tools invoked during execution</p></div>
            </div>
            """, unsafe_allow_html=True)
            tool_html = "".join(f'<span class="tool-badge">⚡ {tc.get("tool", "?")}</span>' for tc in tools)
            st.markdown(tool_html, unsafe_allow_html=True)
            st.json(tools)
    else:
        st.markdown('<div style="text-align:center;color:#444;padding:40px;">Run the agent first to see the execution trace.</div>', unsafe_allow_html=True)

# ── Dashboard Tab ────────────────────────────────────────────────────
with tab_dashboard:
    st.markdown("""
    <div class="section-header">
        <div class="icon blue">📊</div>
        <div class="text"><h3>Dashboard</h3><p>Session statistics and metrics</p></div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.get("history", [])
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{len(history)}</div><div class="stat-label">Recipes</div></div>', unsafe_allow_html=True)
    with s2:
        avg_score = sum(h.get("score", 0) for h in history) / len(history) if history else 0
        st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_score:.0%}</div><div class="stat-label">Avg Score</div></div>', unsafe_allow_html=True)
    with s3:
        avg_lat = sum(h.get("latency", 0) for h in history) / len(history) if history else 0
        st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_lat:.1f}s</div><div class="stat-label">Avg Latency</div></div>', unsafe_allow_html=True)
    with s4:
        grades = [h.get("grade", "?") for h in history]
        best = "A" if "A" in grades else "B" if "B" in grades else "C" if "C" in grades else "D" if "D" in grades else "-"
        st.markdown(f'<div class="stat-card"><div class="stat-value">{best}</div><div class="stat-label">Best Grade</div></div>', unsafe_allow_html=True)

    if history:
        st.markdown("""
        <div class="section-header" style="margin-top:24px;">
            <div class="icon green">📋</div>
            <div class="text"><h3>Recent Runs</h3><p>Last 10 executions</p></div>
        </div>
        """, unsafe_allow_html=True)
        for h in reversed(history[-10:]):
            grade_color = "#22c55e" if h.get("grade") == "A" else "#3b82f6" if h.get("grade") == "B" else "#f59e0b" if h.get("grade") == "C" else "#ef4444"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:8px 12px;background:#0a0a0a;border:1px solid #1a1a1a;border-radius:8px;margin:4px 0;font-size:13px;">
                <span style="color:{grade_color};font-weight:800;font-family:'JetBrains Mono',monospace;">{h.get("grade", "?")}</span>
                <span style="color:#888;">{h.get("score", 0):.0%}</span>
                <span style="color:#444;">|</span>
                <span style="color:#666;">{h.get("type", "?")}</span>
                <span style="color:#444;">|</span>
                <span style="color:#555;font-family:'JetBrains Mono',monospace;">{h.get("latency", 0)}s</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;color:#444;padding:40px;">No runs yet. Generate a recipe to see stats.</div>', unsafe_allow_html=True)

# ── History Tab ──────────────────────────────────────────────────────
with tab_history:
    st.markdown("""
    <div class="section-header">
        <div class="icon red">📋</div>
        <div class="text"><h3>Saved Data</h3><p>Persistent storage</p></div>
    </div>
    """, unsafe_allow_html=True)
    if os.path.exists("shopping_list.json"):
        with open("shopping_list.json") as f:
            items = json.load(f)
        if items:
            st.markdown(f"**🛒 Shopping List ({len(items)} items)**")
            for item in items:
                st.markdown(f'<div class="shop-item"><div class="shop-dot"></div>{item.get("name", "?")} <span style="color:#555;font-size:12px;">({item.get("amount", "")})</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;color:#444;padding:40px;">No saved data yet.</div>', unsafe_allow_html=True)

    if os.path.exists("eval_report.json"):
        with open("eval_report.json") as f:
            report = json.load(f)
        st.markdown(f"""
        <div class="card" style="margin-top:20px;">
            <div style="font-size:16px;font-weight:700;margin-bottom:8px;">🧪 Last Eval Report</div>
            <div style="display:flex;gap:20px;font-size:13px;color:#888;">
                <span>Grade: <b style="color:#f97316;">{report.get("grade", "?")}</b></span>
                <span>Pass Rate: <b style="color:#22c55e;">{report.get("pass_rate", 0):.0%}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)