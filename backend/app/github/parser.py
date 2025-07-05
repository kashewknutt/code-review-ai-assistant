# backend/app/github/parser.py

import os
import ast

def parse_python_file(file_path):
    """Parses a Python file and returns its AST and raw code."""
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    try:
        tree = ast.parse(code, filename=file_path)
        return {"path": file_path, "ast": tree, "code": code}
    except SyntaxError:
        return {"path": file_path, "ast": None, "code": code, "error": "SyntaxError"}

def walk_python_files(directory):
    """Walks through a directory and parses all .py files."""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                results.append(parse_python_file(path))
    return results
