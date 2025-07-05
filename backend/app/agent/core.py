# backend/app/agent/core.py

from langchain.agents import initialize_agent, AgentType
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field
import httpx
import os
from app.agent.memory import get_memory
from app.agent.prompts import DEFAULT_AGENT_PREFIX, DEFAULT_AGENT_SUFFIX


class GitHubChatModel(BaseChatModel):
    temperature: float = Field(default=0.3)
    max_tokens: int = Field(default=256)
    github_token: str = Field(default=os.environ.get("GITHUB_API_TOKEN", None), exclude=True)

    def _convert_message(self, m):
        if isinstance(m, HumanMessage):
            return {"role": "user", "content": m.content}
        elif isinstance(m, AIMessage):
            return {"role": "assistant", "content": m.content}
        else:
            return {"role": "system", "content": m.content}

    def _call(self, messages, **kwargs):
        payload = {
            "model": "openai/gpt-4.1-mini",
            "messages": [self._convert_message(m) for m in messages],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        headers = {
            "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}",
            "Content-Type": "application/json",
        }
        response = httpx.post("https://models.github.ai/inference/chat/completions", json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _generate(self, messages, stop=None, **kwargs):
        content = self._call(messages, **kwargs)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    @property
    def _llm_type(self) -> str:
        return "github-chat-model"


def get_agent(session_id: str, repo_path: str = None, github_token: str = None) -> BaseChatModel:
    print("Get agent called with session_id:", session_id)
    llm = GitHubChatModel(github_token=github_token or os.environ.get("GITHUB_API_TOKEN", None))
    
    from app.agent.tools import get_tools
    tools = get_tools(repo_path, github_token=github_token)
    
    memory = get_memory(session_id)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": DEFAULT_AGENT_PREFIX,
            "suffix": DEFAULT_AGENT_SUFFIX,
        },
    )
    print("Agent initialized")
    return agent
