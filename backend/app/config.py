import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    app_name: str = "RAG OpenAI Chatbot"
    debug: bool = False
    
    model_config = {"env_file": ".env"}

def get_settings():
    return Settings()