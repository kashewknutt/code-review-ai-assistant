# backend/app/analysis/patcher.py

import difflib

def generate_patch(old_code: str, new_code: str, file_path: str) -> str:
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    )

    return "".join(diff)
