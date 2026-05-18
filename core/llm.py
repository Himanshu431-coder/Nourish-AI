"""LLM Factory - Groq for everything (text + vision)."""

import os
import logging

logger = logging.getLogger("nourishai.llm")
_model_cache = {}


def get_llm(model="llama-3.3-70b-versatile", temperature=0.3):
    """Get Groq LLM for text tasks."""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Create .env file with your key.")

    cache_key = f"groq_{model}_{temperature}"
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    from langchain_groq import ChatGroq

    for m in [model, "llama-3.1-8b-instant", "llama3-8b-8192"]:
        try:
            llm = ChatGroq(
                model=m,
                groq_api_key=api_key,
                temperature=temperature,
            )
            _model_cache[cache_key] = llm
            logger.info(f"LLM ready: {m}")
            return llm
        except Exception as e:
            logger.warning(f"Model {m} failed: {e}")
            continue

    raise RuntimeError("No Groq model available")


def get_vision_llm():
    """Get vision-capable LLM. Groq Llama 4 Scout primary, Gemini fallback."""
    from dotenv import load_dotenv
    load_dotenv()

    # Option 1: Groq Llama 4 Scout (active vision model)
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                groq_api_key=groq_key,
                temperature=0.1,
            )
            logger.info("Vision LLM: Groq Llama 4 Scout")
            return llm
        except Exception as e:
            logger.warning(f"Groq vision failed: {e}")

    # Option 2: Gemini fallback (only if Groq fails)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.1,
            )
            logger.info("Vision LLM: Gemini fallback")
            return llm
        except Exception as e:
            logger.warning(f"Gemini vision failed: {e}")

    raise RuntimeError("No vision LLM available. Set GROQ_API_KEY or GEMINI_API_KEY.")