import os
from typing import Callable, ClassVar

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Multi-Agent Optimisation & Harmonisation System"

    # Chosen model based on agents/enums.py
    MODEL_NAME: str = os.getenv("MODEL_NAME", "mistral")

    # Token Limit
    MAX_NEW_TOKENS: int = os.getenv("MAX_NEW_TOKENS", 3000)

    # Huggingface
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

    # Arize Phoenix
    PHOENIX_PROJECT_NAME: str = os.getenv("PHOENIX_PROJECT_NAME", "")
    os.environ["PHOENIX_PROJECT_NAME"] = PHOENIX_PROJECT_NAME

    # Microsoft Azure
    AZURE_OPENAI_API_TYPE: str = os.getenv("AZURE_OPENAI_API_TYPE", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "")
    AZURE_COGNITIVE_SERVICES: str = os.getenv("AZURE_COGNITIVE_SERVICES", "")
    AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_SERVICE: str = os.getenv("AZURE_OPENAI_SERVICE", "")

    AZURE_CREDENTIALS: ClassVar = DefaultAzureCredential()
    AZURE_AD_TOKEN_PROVIDER: Callable = get_bearer_token_provider(
        AZURE_CREDENTIALS, AZURE_COGNITIVE_SERVICES
    )

    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    os.environ["AZURE_OPENAI_API_TYPE"] = AZURE_OPENAI_API_TYPE


settings = Settings()
