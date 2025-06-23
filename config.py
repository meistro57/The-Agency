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
    CODE_MODEL = os.getenv("CODE_MODEL", OLLAMA_MODEL)

    # GPT-4 (for QA Agent)
    GPT4_API_KEY = os.getenv("GPT4_API_KEY", "your-gpt4-api-key")
    GPT4_MODEL = os.getenv("GPT4_MODEL", "gpt-4o")
    GPT4_API_URL = os.getenv("GPT4_API_URL", "https://api.openai.com/v1/chat/completions")

    # MySQL memory system
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "agency")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "agency123")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "the_agency")

    # Paths
    PROJECTS_DIR = os.getenv("PROJECTS_DIR", "./projects")
    LOGS_DIR = os.getenv("LOGS_DIR", "./logs")

    # Containerization
    CONTAINER_TOOL = os.getenv("CONTAINER_TOOL", "docker")

    # Failsafe size limit for generated projects (in MB)
    MAX_PROJECT_DIR_SIZE_MB = int(os.getenv("MAX_PROJECT_DIR_SIZE_MB", 100))

    # Flags
    USE_GPT4_FOR_QA = True
