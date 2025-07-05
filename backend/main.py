import os
from app.agent.core import get_agent
from dotenv import load_dotenv

from app.analysis.linter import run_pylint
from app.analysis.patcher import generate_patch
from app.analysis.suggester import parse_pylint_output
from app.github.parser import walk_python_files
from app.routes import github
from app.github.clone import clone_repo_from_url
from pydantic import BaseModel

from app.agent.tools import load_and_analyze_repo
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
from fastapi import FastAPI

app = FastAPI()

app.include_router(github.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}

class RepoQueryRequest(BaseModel):
    repo_url: str
    session_id: str = "default-session"
    query: str
    github_token: str | None = None

@app.post("/query-repo")
def query_repo(request: RepoQueryRequest):
    try:
        input_string = f"\nQuery: {request.query}\nRepo_URL:{request.repo_url}\n"

        # Let the agent handle the rest
        agent = get_agent(session_id="repo-session", github_token=request.github_token)
        print(f"Running agent for input: {input_string}")
        result = agent.invoke({"input": input_string})

        return {"response": result}

    except Exception as e:
        return {"error": str(e)}



@app.get("/test-agent")
def test_agent():
    agent = get_agent("test-session")
    return {"response": agent.run({"input":"What is Python?"})}

@app.get("/analyze-local")
def analyze_local():
    analysis = walk_python_files("app/")
    return {"files_analyzed": len(analysis)}

@app.get("/lint-local")
def lint_local():
    print("Running linter on local files...")
    files = walk_python_files("app/")
    results = []
    for f in files:
        if f.get("error") is None:
            lint_result = run_pylint(f["path"])
            results.append(lint_result)
    return {"lint_issues": results}

@app.get("/suggestions")
def get_suggestions():
    files = walk_python_files("app/")
    suggestions = []

    for f in files:
        if f.get("error") is None:
            lint = run_pylint(f["path"])
            parsed = parse_pylint_output(lint["output"])
            suggestions.extend(parsed)

    return {"total": len(suggestions), "suggestions": suggestions}

@app.post("/patch")
def get_patch():
    # Simulated change — you'd replace this with actual suggested fixes later
    file_path = "app/main.py"
    old_code = "def foo():\n    pass\n"
    new_code = "def foo():\n    print('Hello')\n"
    
    patch = generate_patch(old_code, new_code, file_path)
    return {"patch": patch}
