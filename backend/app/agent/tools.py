# backend/app/agent/tools.py

import tempfile
from langchain.tools import tool
from app.github.clone import clone_repo_from_url
from app.github import commit_push
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage
from app.analysis import linter, patcher, suggester
from app.utils.text_cleaner import clean_truncate


@tool
def lint_file(path: str) -> str:
    """Run a linter on the given file path and return issues as text."""
    result = linter.run_linter_on_file(Path(path))
    return result

@tool
def suggest_patch(input: str) -> str:
    """
    Given a string in the format: "<file_path>\n<issues>", returns a code patch.
    Example input: "app/main.py\nMissing docstring on line 5"
    """
    try:
        path, issues = input.strip().split("\n", 1)
        return suggester.generate_patch(path, issues)
    except Exception as e:
        return f"Failed to parse input: {e}"

@tool
def apply_patch(input: str) -> str:
    """
    Given input as "<file_path>\n<patch_text>", applies patch to that file.
    """
    try:
        path, patch_text = input.strip().split("\n", 1)
        return patcher.apply_patch_to_file(path, patch_text)
    except Exception as e:
        return f"Failed to apply patch: {e}"


@tool
def get_diff(path: str) -> str:
    """Show diff of the current file with its last committed version."""
    return patcher.generate_diff(path)

@tool
def commit_changes(input: str) -> str:
    """
    Commit and push changes to the given GitHub repo.
    Input format: "<repo_path>\n<commit_message>"
    """
    try:
        repo_path, commit_message = input.strip().split("\n", 1)
        return commit_push.commit_and_push(repo_path, commit_message)
    except Exception as e:
        return f"Failed to parse input: {e}"

@tool
def load_and_analyze_repo(input: str) -> str:
    """
    Clone a GitHub repo and answer a question about it.
    Input format: "<repo_url>\n<question>"
    """
    import os
    print("Received input:", input)

    try:
        # Split input into repo_url and question
        parts = input.strip().split("\n", 1)
        if len(parts) < 2:
            return "Invalid input format. Expected '<repo_url>\\n<question>'"
        
        repo_url, question = parts
        print("Repo URL:", repo_url)
        print("Question:", question)

        # Clone the repository
        with tempfile.TemporaryDirectory() as tmpdir:
            from app.agent.core import GitHubChatModel
            local_path = Path(tmpdir) / "repo"
            print(f"Cloning repo from: {repo_url} to {local_path}")
            clone_repo_from_url(repo_url, str(local_path))

            # Extended list of common files in diverse stacks
            files_to_check = [
                # Documentation
                "README.md", "readme.md",

                # Entry points & common frontend
                "index.html", "public/index.html",
                "src/index.js", "src/index.tsx",
                "src/main.tsx", "src/main.js",
                "src/App.js", "src/App.tsx",
                "src/app.tsx", "src/app.jsx",

                # Configs
                "vite.config.js", "next.config.js",
                "package.json", "tsconfig.json",

                # Backend
                "main.py", "app.py",
                "server.js", "index.js",
                "src/server.js", "backend/server.js",
                "api/index.js", "api/main.py",

                # Pages (Next.js)
                "pages/index.js", "pages/index.tsx",

                # Svelte
                "src/App.svelte", "src/main.ts",

                # Monorepo roots
                "apps/app/index.tsx", "packages/ui/src/index.tsx",
            ]

            collected = []
            print("Checking files in repo...")
            for file_name in files_to_check:
                file_path = local_path / file_name
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    collected.append(f"## {file_name}\n{content[:2000]}")
                    print(f"Found file: {file_name}")
            
            # If files found, proceed to use them
            if collected:
                print(f"Collected {len(collected)} files.")
                repo_summary = "\n\n".join(collected)
                llm = GitHubChatModel(max_tokens=512)
                print("Calling LLM to answer the question...")
                summary_prompt = f"""
You are an expert software assistant helping users understand GitHub repositories.

Here are some key files from the repo:
{repo_summary}

Based on this, answer the following question in clear, natural English:

{question}
                """
                response = llm._call([
                    HumanMessage(content=summary_prompt)
                ])

                return clean_truncate(response)

            # Hail Mary Mode: No useful files found
            file_tree = []
            print("No useful files found. Walking through directory structure...")
            for root, dirs, files in os.walk(local_path):
                for name in files:
                    rel_path = os.path.relpath(os.path.join(root, name), local_path)
                    file_tree.append(rel_path)

            if not file_tree:
                return "Cloned the repo, but it appears to be empty."

            print(f"File tree found with {len(file_tree)} files.")
            tree_text = "\n".join(file_tree)
            llm = GitHubChatModel()
            # Ask LLM which files to try opening
            print("Calling LLM to analyze file tree...")
            tool_response = llm._call([
                SystemMessage(content="You are an expert developer. Given a file tree, identify the most useful files to read to understand this codebase."),
                HumanMessage(content=f"File tree:\n{tree_text}"),
                HumanMessage(content="List up to 5 files you recommend reading to get an overview of this repo. Respond with only their relative paths, one per line.")
            ])

            paths = tool_response.strip().splitlines()
            selected_files = []
            print("LLM suggested the following files:", paths)
            for rel_path in paths:
                try:
                    abs_path = local_path / rel_path.strip()
                    if abs_path.exists():
                        content = abs_path.read_text(encoding="utf-8", errors="ignore")
                        selected_files.append(f"## {rel_path}\n{content[:2000]}")
                        print(f"Selected file: {rel_path}")
                except Exception as e:
                    print(f"Error reading file {rel_path}: {e}")
                    continue

            if not selected_files:
                return "Tried inspecting files from the LLM suggestion but couldn't read them."

            print(f"Final selected {len(selected_files)} files.")
            final_summary = "\n\n".join(selected_files)
            print("Calling LLM with final selected files...")
            final_response = llm._call([
                SystemMessage(content="You are a code assistant. Given these files, answer the question."),
                HumanMessage(content=f"Repo files:\n{final_summary}"),
                HumanMessage(content=f"Question: {question}")
            ])
            return final_response

    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Failed to analyze repo: {e}"


def get_tools(repo_path=None):
    base_tools = [
        lint_file,
        suggest_patch,
        apply_patch,
        get_diff,
        commit_changes,
        load_and_analyze_repo
    ]

    if not repo_path:
        return base_tools

    from app.github.parser import walk_python_files

    @tool
    def list_repo_files(input: str) -> str:
        """List all Python files in the current cloned repo. Input is ignored."""
        print("Input to list_repo_files", input)
        files = walk_python_files(repo_path)
        return "\n".join(f["path"] for f in files if f.get("error") is None)

    @tool
    def read_file_content(path: str) -> str:
        """Read contents of a file at the given path within the repo."""
        try:
            full_path = Path(path)
            if not full_path.is_absolute():
                full_path = Path(repo_path) / path
            return full_path.read_text(encoding="utf-8", errors="ignore")[:4000]  # limit to 4K
        except Exception as e:
            return f"Error reading file: {e}"

    return base_tools + [list_repo_files, read_file_content]