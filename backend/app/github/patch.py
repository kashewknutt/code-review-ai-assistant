import os
from unidiff import PatchSet

def apply_patch_to_repo(repo_path: str, patch_str: str):
    patch = PatchSet(patch_str.splitlines(keepends=True))
    
    for patched_file in patch:
        file_path = os.path.join(repo_path, patched_file.path)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for hunk in reversed(patched_file):
            start = hunk.source_start - 1
            end = start + hunk.source_length
            lines[start:end] = [l.value for l in hunk if l.is_added or l.is_context]

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
