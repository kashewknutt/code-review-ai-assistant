import httpx
import re

GITHUB_API_URL = "https://api.github.com"

def parse_github_url(url: str):
    """
    Takes a GitHub repo URL and returns (owner, repo)
    """
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if not match:
        raise ValueError("Invalid GitHub repo URL.")
    
    owner, repo = match.groups()
    
    if repo.endswith(".git"):
        repo = repo[:-4]
    
    return owner, repo

def get_repo_contents(owner: str, repo: str, path: str = ""):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

def get_branches(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

def get_repo_metadata(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()
