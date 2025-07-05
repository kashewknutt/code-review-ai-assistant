import re
def clean_truncate(text, max_chars=4000):
    truncated = text[:max_chars]
    # Try to end at last full sentence if cut
    match = re.search(r"(.*?[.!?])\s", truncated[::-1])
    if match:
        cutoff = len(truncated) - match.end() + 1
        return truncated[:cutoff].strip()
    return truncated.strip()