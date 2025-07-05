# backend/app/analysis/patcher.py

import difflib
from pathlib import Path
import subprocess

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

def apply_patch_to_file(file_path: str, patch_text: str) -> str:
    """
    Applies a unified diff patch to the given file.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"

        original_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        patched_lines = list(difflib.restore(patch_text.splitlines(keepends=True), which=1))

        diff = list(difflib.unified_diff(original_lines, patched_lines, lineterm=""))
        if not diff:
            return "Patch does not introduce any changes."
        
        new_content = "".join(patched_lines)
        path.write_text(new_content, encoding="utf-8")

        return f"Patch applied successfully to {file_path}"
    except Exception as e:
        return f"Failed to apply patch: {e}"
    
def generate_diff(file_path: str) -> str:
    """
    Generates a unified diff between the current file and the last committed version.
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    try:
        # Get last committed version from Git
        result = subprocess.run(
            ["git", "show", f"HEAD:{file_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        committed_code = result.stdout.splitlines(keepends=True)

        # Read current file content
        current_code = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)

        # Generate unified diff
        diff = difflib.unified_diff(
            committed_code,
            current_code,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )

        return "".join(diff) or "No differences with last committed version."

    except subprocess.CalledProcessError as e:
        return f"Failed to get committed version: {e.stderr.strip()}"
    except Exception as e:
        return f"Error generating diff: {e}"
