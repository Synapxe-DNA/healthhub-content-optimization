from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from pathlib import Path
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

# Substitute <project_root> with the [root folder for your project](https://docs.kedro.org/en/stable/tutorial/spaceflights_tutorial.html#terminology)
conf_path = str(Path("./") / settings.CONF_SOURCE)

# Load the credentials
conf_loader = OmegaConfigLoader(conf_source=conf_path)
credentials = conf_loader["credentials"]

azure_credentials = credentials["azure_credentials"]
api_version = azure_credentials["API_VERSION"]
azure_endpoint = azure_credentials["AZURE_ENDPOINT"]
cognitive_services = azure_credentials["COGNITIVE_SERVICES"]

def ask(html_content: str) -> str:
    azure_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        azure_credential, cognitive_services
    )

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
        model="chat",
        temperature=0.0,
        max_tokens=2000,
        n=1,
        seed=1234,
    )

    return response.choices[0].message.content
