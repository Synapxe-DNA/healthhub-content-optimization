import getpass
import os
import dotenv
from langchain_huggingface import HuggingFaceEndpoint
from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.conversation.base import ConversationChain
from prompt import LLMPrompts


dotenv.load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"]= os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"

MODEL_NAME = 'llama3'
ROLES = ['Researcher', "Compiler"]

prompts = LLMPrompts()
ans = prompts.return_researcher_prompt()

class LLMInterface(ABC):
    @abstractmethod
    def generate_text(self, question, context):
        pass

class Llama(LLMInterface):
    def __init__(self, model, prompt_template, role):
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def generate_text(self, article = " "):
        if self.role == "Researcher":
            prompt_t = PromptTemplate.from_template(self.prompt_template)
            chain = LLMChain(
                llm=self.model,
                prompt = prompt_t)        
            print("generating keypoints")
            response1 = chain.invoke({"Article": article})
            print("keypoints generated")
            answer = response1['text']
            return answer
        else:
            return "This node cannot run generate_text()"
    
    def generate_article(self, keypoints1, keypoints2):
        if self.role == "Compiler":
            prompt_t = PromptTemplate.from_template(self.prompt_template)
            chain = LLMChain(
                llm=self.model,
                prompt = prompt_t)        
            response1 = chain.invoke({"KP1": keypoints1, "KP2" : keypoints2})
            answer = response1['text']
            return answer
        else:
            return "This node cannot run generate_article()"
        
