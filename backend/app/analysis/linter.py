# backend/app/analysis/linter.py

import subprocess

def run_pylint(file_path):
    """Runs pylint on a single file and returns the raw output."""
    try:
        result = subprocess.run(
            ["pylint", file_path, "-rn", "--score=n"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {"file": file_path, "output": result.stdout, "errors": result.stderr}
    except subprocess.TimeoutExpired:
        return {"file": file_path, "output": "", "errors": "Timeout"}

def run_linter_on_file(file_path: str) -> str:
    """
    Wrapper for running the linter and formatting the result as plain text.
    """
    result = run_pylint(file_path)

    output = result.get("output", "")
    errors = result.get("errors", "")

    if errors:
        return f"⚠️ Linter Errors:\n{errors.strip()}\n\n📄 Linter Output:\n{output.strip()}"
    elif not output.strip():
        return f"✅ No lint issues found in {file_path}"
    else:
        return f"📄 Linter Output for {file_path}:\n{output.strip()}"