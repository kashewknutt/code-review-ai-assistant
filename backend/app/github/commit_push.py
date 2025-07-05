from app.github.client import parse_github_url
from github import Github

def commit_patch_and_create_pr(
    token: str,
    repo_url: str,
    patch_branch: str,
    commit_msg: str,
    pr_title: str,
    pr_body: str,
    file_changes: list[dict]  # Each dict: {'path': str, 'content': str, 'message': Optional[str]}
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
