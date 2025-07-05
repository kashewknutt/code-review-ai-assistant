# backend/app/agent/memory.py

from langchain.memory import ConversationBufferMemory

def get_memory(session_id: str):
    return ConversationBufferMemory(memory_key="chat_history", return_messages=True)
