import os
from typing import Callable, ClassVar

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Configuration settings for the Multi-Agent Optimisation & Harmonisation System.

    This class defines application-wide settings, including API tokens, model configurations,
    and integration with various services such as Huggingface, Microsoft Azure, and Arize Phoenix.

    Attributes:
        APP_NAME (str): The name of the application.
        MODEL_NAME (str): The name of the model to be used, defaulting to "mistral" if not set via environment variables.
        MAX_NEW_TOKENS (int): The maximum number of tokens allowed, defaulting to 3000 if not set via environment variables.
        HUGGINGFACEHUB_API_TOKEN (str): API token for Huggingface Hub, set from environment variables.
        AZURE_OPENAI_API_TYPE (str): Azure OpenAI API type, set from environment variables.
        AZURE_OPENAI_API_VERSION (str): Azure OpenAI API version, set from environment variables.
        AZURE_COGNITIVE_SERVICES (str): Azure Cognitive Services name, set from environment variables.
        AZURE_DEPLOYMENT_NAME (str): Name of the Azure deployment, set from environment variables.
        AZURE_OPENAI_ENDPOINT (str): Azure OpenAI endpoint URL, set from environment variables.
        AZURE_OPENAI_SERVICE (str): Name of the Azure OpenAI service, set from environment variables.
        AZURE_CREDENTIALS (ClassVar): Azure credentials object, using `DefaultAzureCredential`.
        AZURE_AD_TOKEN_PROVIDER (Callable): Function to get a bearer token provider for Azure AD, using the Azure credentials.
        PHOENIX_PROJECT_NAME (str): Project name for Arize Phoenix, defaulting to the Azure deployment name if not set via environment variables.
    """

    # App Settings
    APP_NAME: str = "Multi-Agent Optimisation & Harmonisation System"

    # Chosen model based on agents/enums.py
    MODEL_NAME: str = os.getenv("MODEL_NAME", "mistral")

    # Token Limit
    MAX_NEW_TOKENS: int = os.getenv("MAX_NEW_TOKENS", 4000)

    # Huggingface API token setup
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

    # Microsoft Azure settings
    AZURE_OPENAI_API_TYPE: str = os.getenv("AZURE_OPENAI_API_TYPE", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "")
    AZURE_COGNITIVE_SERVICES: str = os.getenv("AZURE_COGNITIVE_SERVICES", "")
    AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_SERVICE: str = os.getenv("AZURE_OPENAI_SERVICE", "")

    # Initialize Azure credentials and token provider
    AZURE_CREDENTIALS: ClassVar = DefaultAzureCredential()
    AZURE_AD_TOKEN_PROVIDER: Callable = get_bearer_token_provider(
        AZURE_CREDENTIALS, AZURE_COGNITIVE_SERVICES
    )

    # Setting up environment variables for Azure
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    os.environ["AZURE_OPENAI_API_TYPE"] = AZURE_OPENAI_API_TYPE

    # Arize Phoenix project name setup
    PHOENIX_PROJECT_NAME: str = os.getenv("PHOENIX_PROJECT_NAME", AZURE_DEPLOYMENT_NAME)
    os.environ["PHOENIX_PROJECT_NAME"] = PHOENIX_PROJECT_NAME


# Instantiate the settings object
settings = Settings()
