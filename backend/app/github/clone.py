import os
import shutil
import tempfile
import subprocess
import requests
from urllib.parse import urlparse
from app.github.client import parse_github_url

def download_public_repo(repo_url: str, branch="main") -> str:
    owner, repo = parse_github_url(repo_url)
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, f"{repo}.zip")

    with requests.get(zip_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    shutil.unpack_archive(zip_path, tmp_dir)
    os.remove(zip_path)

    extracted_path = os.path.join(tmp_dir, f"{repo}-{branch}")
    return extracted_path

def clone_private_repo(repo_url: str, github_token: str) -> str:
    tmp_dir = tempfile.mkdtemp()
    parsed = urlparse(repo_url)
    url_with_auth = f"https://{github_token}@{parsed.netloc}{parsed.path}"

    subprocess.run(
        ["git", "clone", "--depth=1", url_with_auth, tmp_dir],
        check=True
    )

    return tmp_dir

def clone_repo_from_url(repo_url: str, target_path: str) -> None:
    """
    Clone a public or private GitHub repo into the given target path.
    Will use requests+unzip for public, and `git clone` for private (token via env).
    """
    try:
        # Try public clone first
        extracted_path = download_public_repo(repo_url)

        # Move contents to target_path
        shutil.copytree(extracted_path, target_path, dirs_exist_ok=True)
    except Exception as public_error:
        # If public clone fails, try private clone (requires GITHUB_API_TOKEN in env)
        github_token = os.environ.get("GITHUB_API_TOKEN")
        if not github_token:
            raise RuntimeError("Failed to clone repo publicly, and no GITHUB_API_TOKEN set for private clone.") from public_error

        try:
            tmp_dir = clone_private_repo(repo_url, github_token)
            shutil.copytree(tmp_dir, target_path, dirs_exist_ok=True)
        except Exception as private_error:
            raise RuntimeError("Failed to clone GitHub repo (public and private attempts failed).") from private_error
