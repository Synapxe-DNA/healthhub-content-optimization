from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


def ask(html_content: str) -> str:
    azure_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        azure_credential, "https://cognitiveservices.azure.com/.default"
    )

    openai_client = AzureOpenAI(
        api_version="2024-03-01-preview",
        azure_endpoint="https://cog-zicuh2lqrbb2s.openai.azure.com",
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
