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
