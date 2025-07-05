# backend/app/agent/tools.py

from langchain.tools import tool

@tool
def dummy_tool(text: str) -> str:
    """Echoes back the input text"""
    return f"You said: {text}"
