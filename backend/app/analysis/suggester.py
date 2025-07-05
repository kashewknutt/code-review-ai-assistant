# backend/app/analysis/suggester.py

import re
from typing import List, Dict
from pathlib import Path
from app.agent.core import GitHubChatModel
from langchain_core.messages import HumanMessage

def parse_pylint_output(output: str) -> List[Dict]:
    suggestions = []
    lines = output.strip().split("\n")

    for line in lines:
        # Pylint typical format: path:line:col: message (error code)
        match = re.match(r"(.+?):(\d+):\d+: (.+?) \((.+?)\)", line)
        if match:
            file_path, line_num, message, code = match.groups()
            suggestions.append({
                "file": file_path.strip(),
                "line": int(line_num),
                "message": message.strip(),
                "code": code,
                "type": categorize_lint(code)
            })
    return suggestions

def categorize_lint(code: str) -> str:
    if code.startswith("E"):
        return "Error"
    elif code.startswith("W"):
        return "Warning"
    elif code.startswith("C"):
        return "Convention"
    elif code.startswith("R"):
        return "Refactor"
    else:
        return "Info"
    
def generate_patch(file_path: str, issues: str) -> str:
    """
    Given a file path and issue description, use the LLM to suggest a fix and return a patch.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"❌ File not found: {file_path}"

        original_code = path.read_text(encoding="utf-8", errors="ignore")

        prompt = f"""
You are a senior software engineer assisting with code linting and fixing.

Below is the original code from `{file_path}`:
```python
{original_code[:4000]}
The following linting issue(s) were detected:
{issues}

Please return the full corrected version of the code after fixing the issue(s). Do not explain — just return the fixed code.
"""
        llm = GitHubChatModel()
        fixed_code = llm._call([HumanMessage(content=prompt)]).strip()

        if not fixed_code or fixed_code == original_code:
            return "No changes suggested by the model."

        patch = generate_patch(original_code, fixed_code, file_path)
        return patch or "Diff could not be generated. No differences found."

    except Exception as e:
        return f"Failed to generate patch: {e}"
