import getpass
import os
import dotenv
from langchain_huggingface import HuggingFaceEndpoint
from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.conversation.base import ConversationChain
from langchain_core.output_parsers import StrOutputParser
from prompt import prompt_tool


dotenv.load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"]= os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"

MODELS = ["meta-llama/Meta-Llama-3-8B-Instruct", "microsoft/Phi-3-mini-128k-instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
MAX_NEW_TOKENS = 3000

def start_llm(model, role):
    if model == "Mistral":
        model_prompter = prompt_tool(model= model)
        llm = HuggingFaceEndpoint(endpoint_url=MODELS[2], max_new_tokens=MAX_NEW_TOKENS)
        return Mistral(llm, model_prompter, role)
    elif model == "Llama3":
        model_prompter = prompt_tool(model)
        llm = HuggingFaceEndpoint(endpoint_url=MODELS[0], max_new_tokens=MAX_NEW_TOKENS)
        return Llama(llm, model_prompter, role)
    else:
        return "Your model does not exist"
    pass



class LLMInterface(ABC):
    @abstractmethod
    def generate_text(self, question, context):
        pass

    @abstractmethod
    def compile_points(self, keypoints):
        pass

class Llama(LLMInterface):
    def __init__(self, model, prompt_template, role):
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def generate_text(self, article : str):
        if self.role == "Researcher":
            prompt_t = PromptTemplate(input_variables=["Article"], template=self.prompt_template.return_researcher_prompt())
            chain = prompt_t | self.model | StrOutputParser()
            print("generating keypoints")
            response = chain.invoke(article)
            print("keypoints generated")
            answer = response['text']
            return answer
        else:
            return "This node cannot run generate_text()"
    
    def compile_points(self, keypoints: list = []):
        if self.role == "Comparer":
            prompt_t = PromptTemplate.from_template(self.prompt_template.return_comparer_prompt())
            chain = LLMChain(
                llm=self.model,
                prompt = prompt_t)        
            response1 = chain.invoke({"Keypoints" : keypoints})
            answer = response1['text']
            return answer
        else:
            return "This node cannot run generate_article()"

class Mistral(LLMInterface):
    def __init__(self, model, prompt_template, role):
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def generate_text(self, article : str):
        if self.role == "Researcher":
            prompt_t = PromptTemplate(input_variables=["Article"], template=self.prompt_template.return_researcher_prompt())
            chain = prompt_t | self.model | StrOutputParser()
            print("generating keypoints")
            response = chain.invoke(article)
            print("keypoints generated")
            return response
        else:
            return "This node cannot run generate_text()"
    
    def compile_points(self, keypoints: list = []):
        if self.role == "Comparer":
            prompt_t = PromptTemplate.from_template(self.prompt_template.return_compiler_prompt())
            if len(keypoints) >= 2:
                input_keypoints = "--START OF KEYPOINTS--"
                for index in range(len(keypoints)):
                    input_keypoints += f"\n Article {index + 1} keypoints:\n"
                    input_keypoints += f"\n {keypoints[index]}\n"
                input_keypoints += "\n --END OF KEYPOINTS--"
                chain = prompt_t | self.model
                response = chain.invoke({"Keypoints" : input_keypoints})
                return response
            else:
                return "There are insufficient number of keypoints to compare. Kindly add more articles to compare and try again."
        else:
            return "This node cannot run generate_article()"