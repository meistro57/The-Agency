# config.py
from dotenv import load_dotenv
load_dotenv()

import os

class Config:
    # Local model via Ollama
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:7b")
    # Default to the chat endpoint for Ollama's API
    OLLAMA_API_URL = os.getenv(
        "OLLAMA_API_URL", "http://localhost:11434/api/chat"
    )
    # Default to OpenAI's GPT-4o for wider compatibility. Override with
    # `CODE_MODEL=$OLLAMA_MODEL` if a local Ollama model is available.
    CODE_MODEL = os.getenv("CODE_MODEL", "gpt-4o")

    # GPT-4 (for QA Agent)
    GPT4_API_KEY = os.getenv("GPT4_API_KEY", "your-gpt4-api-key")
    GPT4_MODEL = os.getenv("GPT4_MODEL", "gpt-4o")
    GPT4_API_URL = os.getenv("GPT4_API_URL", "https://api.openai.com/v1/chat/completions")

    # Anthropic (optional)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    # SQLite memory system
    # Path to the local SQLite database used for persistent memory.
    SQLITE_PATH = os.getenv("SQLITE_PATH", "the_agency.db")

    # Paths
    PROJECTS_DIR = os.getenv("PROJECTS_DIR", "./projects")
    LOGS_DIR = os.getenv("LOGS_DIR", "./logs")

    # Containerization
    CONTAINER_TOOL = os.getenv("CONTAINER_TOOL", "docker")

    # Failsafe size limit for generated projects (in MB)
    MAX_PROJECT_DIR_SIZE_MB = int(os.getenv("MAX_PROJECT_DIR_SIZE_MB", 100))

    # Flags
    USE_GPT4_FOR_QA = True
