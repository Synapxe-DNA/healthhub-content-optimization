from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from kedro.config import MissingConfigException, OmegaConfigLoader
from kedro.framework.project import settings
from openai import AzureOpenAI

# Substitute <project_root> with the [root folder for your project](https://docs.kedro.org/en/stable/tutorial/spaceflights_tutorial.html#terminology)
conf_path = str(Path("./") / settings.CONF_SOURCE)

# Load the credentials
conf_loader = OmegaConfigLoader(conf_source=conf_path)
try:
    credentials = conf_loader["credentials"]
# When credentials.yml is not created locally
except MissingConfigException:
    # Use dummy credentials, in order to kedro viz azure_rag pipeline on GitHub page
    print(
        "Using dummy credentials for kedro viz. If running azure_rag pipeline, please create credentials.yml."
    )
    dummy_credentials = {
        "azure_credentials": {
            "api_version": "2024-01-01",
            "azure_endpoint": "dummy-azure-endpoint",
            "cognitive_services": "dummy-cognitive-service-key",
            "model_deployment": "dummy-model-deployment-id",
        }
    }
    credentials = dummy_credentials

azure_credentials = credentials.get("azure_credentials", {})
api_version = azure_credentials.get("api_version", "")
azure_endpoint = azure_credentials.get("azure_endpoint", "")
cognitive_services = azure_credentials.get("cognitive_services", "")
model_deployment = azure_credentials.get("model_deployment", "")


def ask(
    html_content: str,
    temperature: int,
    max_tokens: int,
    n_completions: int,
    seed: int,
) -> str:
    azure_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(azure_credential, cognitive_services)

    openai_client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        azure_ad_token_provider=token_provider,
    )

    prompt = """
    Below is the given full article html, extract the content of the tables, including any descriptions about the tables or may be helpful for the user to understand the tables.
    Do not retain any of the text that are not helpful for the tables, remove all html tags and replace them with markdown format.
    Output the response as a single, readable string without any other sentences needed.

    {html_content}
    """

    query_messages = [
        {
            "role": "system",
            "content": "You are an AI assistant specialized in extracting structured content from HTML.",
        },
        {"role": "user", "content": prompt.format(html_content=html_content)},
    ]

    response = openai_client.chat.completions.create(
        messages=query_messages,
        model=model_deployment,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n_completions,
        seed=seed,
    )

    return response.choices[0].message.content
