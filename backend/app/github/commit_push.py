## backend/app/github/commit_push.py

from pathlib import Path
import subprocess
from app.github.client import parse_github_url
from github import Github
import base64
import httpx
import os

def commit_patch_and_create_pr(
    token: str,
    repo_url: str,
    patch_branch: str,
    commit_msg: str,
    pr_title: str,
    pr_body: str,
    file_changes: list[dict]
) -> str:
    """
    Commits changes and opens a PR via PyGithub.

    Args:
        token: GitHub token.
        repo_url: Full repo URL.
        patch_branch: Name of the new branch.
        commit_msg: Commit message.
        pr_title: Title of the PR.
        pr_body: Description of the PR.
        file_changes: List of dicts with keys: 'path', 'content', and optional 'message'.

    Returns:
        URL of the created PR.
    """
    owner, repo_name = parse_github_url(repo_url)
    gh = Github(token)
    repo = gh.get_repo(f"{owner}/{repo_name}")
    default_branch = repo.default_branch

    # Create a new branch from default
    source = repo.get_branch(default_branch)
    repo.create_git_ref(ref=f"refs/heads/{patch_branch}", sha=source.commit.sha)

    # Commit file changes
    for file in file_changes:
        path = file['path']
        content = file['content']
        message = file.get('message', commit_msg)

        try:
            # Check if the file exists
            existing_file = repo.get_contents(path, ref=patch_branch)
            repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch=patch_branch
            )
        except Exception:
            # If file doesn't exist, create it
            repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=patch_branch
            )

    # Create PR
    pr = repo.create_pull(
        title=pr_title,
        body=pr_body,
        head=patch_branch,
        base=default_branch
    )

    return pr.html_url

def update_file(
    repo_owner: str,
    repo_name: str,
    file_path: str,
    new_content: str,
    commit_message: str,
    branch: str = "main",
    github_token: str = None,
) -> dict:
    """
    Update a file in a GitHub repo with a new commit.

    Returns GitHub API response dict.
    """
    token = github_token or os.getenv("GITHUB_API_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Step 1: Get the file's current SHA
    file_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    resp = httpx.get(file_url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch file metadata: {resp.status_code} {resp.text}")
    file_info = resp.json()
    current_sha = file_info["sha"]

    # Step 2: Prepare commit data
    data = {
        "message": commit_message,
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": current_sha,
        "branch": branch,
    }

    # Step 3: PUT update request
    put_resp = httpx.put(file_url, json=data, headers=headers)
    if put_resp.status_code not in [200, 201]:
        raise Exception(f"Failed to update file: {put_resp.status_code} {put_resp.text}")

    return put_resp.json()

def commit_and_push(repo_path: str, commit_message: str) -> str:
    """
    Commits all staged changes in the local Git repo and pushes to origin.
    
    Args:
        repo_path: Local path to the Git repository.
        commit_message: Commit message.

    Returns:
        Output log or error message.
    """
    repo_path = Path(repo_path).resolve()

    if not repo_path.is_dir():
        return f"Path does not exist or is not a directory: {repo_path}"

    git_cmds = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push"]
    ]

    output_log = []

    for cmd in git_cmds:
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            output_log.append(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            # Don't fail on empty commit
            if "nothing to commit" in e.stderr:
                return "Nothing to commit. Working tree clean."
            return f"Error running {' '.join(cmd)}:\n{e.stderr.strip()}"

    return "Changes committed and pushed.\n" + "\n".join(output_log)