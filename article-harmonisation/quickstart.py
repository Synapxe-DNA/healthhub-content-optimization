import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE", "")
AZURE_COGNITIVE_SERVICES = os.getenv("AZURE_COGNITIVE_SERVICES", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "")

azure_credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    azure_credential,
    AZURE_COGNITIVE_SERVICES,
)

client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com/",
    azure_ad_token_provider=token_provider,
)

# Send a completion call to generate an answer
print("Sending a test completion job")
prompt = "Write a tagline for an ice cream shop. "
response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,
    messages=[{"role": "system", "content": prompt}],
    temperature=1,
    max_tokens=10,
    top_p=0.5,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
)


if __name__ == "__main__":
    print(prompt + response.choices[0].message.content)
