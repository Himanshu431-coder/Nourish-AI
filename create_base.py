import os

# All files and their content
FILES = {}

# ÄÄÄ requirements.txt ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ
FILES["requirements.txt"] = """streamlit^>=1.40.0
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-google-genai>=2.0.0
google-generativeai>=0.8.0
chromadb>=0.5.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
gTTS>=2.5.0
Pillow>=10.0.0
python-dotenv>=1.0.0
mcp>=1.0.0
streamlit-option-menu>=0.3.6
"""

# ÄÄÄ .env.example ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ
FILES[".env.example"] = """GEMINI_API_KEY=your_gemini_api_key_here
"""

# ÄÄÄ .gitignore ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ
FILES[".gitignore"] = """__pycache__/
*.pyc
.env
*.db
chroma_db/
*.mp3
shopping_list.json
eval_report.json
.venv/
venv/
"""

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip())
    print(f"Created: {path}")

print("\n? Base files created!")
