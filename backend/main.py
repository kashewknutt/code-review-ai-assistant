import os
from backend.app.agent.core import get_agent
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/test-agent")
def test_agent():
    agent = get_agent("test-session")
    return {"response": agent.run("What is Python?")}
