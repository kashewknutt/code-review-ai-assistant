# backend/app/analysis/suggester.py

import re
from typing import List, Dict

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
