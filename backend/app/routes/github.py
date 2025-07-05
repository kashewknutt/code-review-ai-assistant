from typing import Optional
import uuid
from fastapi import APIRouter, Query
from app.github.client import parse_github_url, get_branches, get_repo_contents, get_repo_metadata
from app.github.clone import clone_private_repo, download_public_repo
from app.github.patch import apply_patch_to_repo
from app.github.commit_push import commit_patch_and_create_pr

router = APIRouter()

@router.get("/github/info")
def get_repo_info(repo_url: str = Query(..., description="GitHub repo URL")):
    owner, repo = parse_github_url(repo_url)
    meta = get_repo_metadata(owner, repo)
    return {
        "owner": owner,
        "repo": repo,
        "default_branch": meta.get("default_branch"),
        "description": meta.get("description"),
        "private": meta.get("private")
    }

@router.get("/github/branches")
def get_repo_branches(repo_url: str):
    owner, repo = parse_github_url(repo_url)
    return get_branches(owner, repo)

@router.get("/github/files")
def get_repo_files(repo_url: str, path: str = ""):
    owner, repo = parse_github_url(repo_url)
    return get_repo_contents(owner, repo, path)

@router.post("/github/pr")
def handle_patch_and_pr(repo_url: str, patch: str, token: Optional[str] = None):
    if token:
        path = clone_private_repo(repo_url, token)
    else:
        path = download_public_repo(repo_url)

    apply_patch_to_repo(path, patch)

    if not token:
        return {"status": "Patch applied locally (public mode)"}

    pr_url = commit_patch_and_create_pr(
        token=token,
        repo_url=repo_url,
        patch_branch="auto-patch-" + str(uuid.uuid4())[:8],
        commit_msg="fix: automated patch",
        pr_title="Suggested Fix from AI",
        pr_body="This PR was generated from an automated analysis of the repo."
    )

    return {"status": "PR created", "url": pr_url}

