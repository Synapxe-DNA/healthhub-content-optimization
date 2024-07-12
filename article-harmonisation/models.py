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

def start_llm(model:str , role: str):
    """Starts up and returns an instance of a specific model type 

    Args: 
        model: a String input stating the model used
        role: a String input stating the role of the model. List of model roles can be found under NODE_ROLES in harmonisation.py
    
    Returns:
        an object from the model class pertaining to the string input
    
    Raises:
        ValueError: if the input model is not supported, yet
    """
    if model == "Mistral":
        # creating an instance of a LLMPrompt object based on the model used
        model_prompter = prompt_tool(model= model)
        # starting an instance of the model using HuggingFaceEndpoint
        llm = HuggingFaceEndpoint(endpoint_url=MODELS[2], max_new_tokens=MAX_NEW_TOKENS)
        return Mistral(llm, model_prompter, role)
    elif model == "Llama3":
        # creating an instance of a LLMPrompt object based on the model used
        model_prompter = prompt_tool(model)
        # starting an instance of the model using HuggingFaceEndpoint
        llm = HuggingFaceEndpoint(endpoint_url=MODELS[0], max_new_tokens=MAX_NEW_TOKENS)
        return Llama(llm, model_prompter, role)
    else:
        raise ValueError(f"You entered {model}, which is not a support model type")

class LLMInterface(ABC):
    """Abstract class for all LLM classes. Each unique LLM model will have it's own LLM class, which must inherit from this class, hence they must all include the following methods.

    This class inherits from ABC class.

    """
    @abstractmethod
    def generate_text(self, article):
        """ Abstract method for generating and returing a summary of keypoints based on the article
        Args: 
            article: String input of the article to be summarised
        """
        pass

    @abstractmethod
    def compile_points(self, keypoints):
        """ Abstract method for compiling and returing from a list of keypoints
        Args: 
            keypoints: list input of the article keypoints to be compiled
        """
        pass

class Llama(LLMInterface):
    """This class contains the methods for the Llama3 class. It inherits from the LLMInterface abstract class.
        
        Attributes:
            model: a HuggingFaceEndpoint object for the specific model
            prompt_template: a LLMPrompt object for the specific model
            role: a String dictating the role of the llm

    """
    def __init__(self, model, prompt_template, role):
        """Initializes the instance based on model, prompt_template and role input.

        Args:
          model: determines the model, in this case it will be a Llama3 model
          prompt_template: the specific prompt template for the model and its role
          role: determines the role of the model in the article harmonisation process
        """
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def generate_text(self, article : str):
        """ Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".
        
        Args:
            article: a String input of the article content
        
        Returns:
            answer: a String containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.

        """
        if self.role == "Researcher":
            prompt_t = PromptTemplate(input_variables=["Article"], template=self.prompt_template.return_researcher_prompt())
            chain = prompt_t | self.model | StrOutputParser()
            print("generating keypoints")
            response = chain.invoke(article)
            print("keypoints generated")
            answer = response['text']
            return answer
        else:
            raise TypeError(f"This node is a {self.role} node and cannot run generate_text()")
    
    def compile_points(self, keypoints: list = []):
        """ A list of keypoints from different articles are compiled using this method. This is the second step in the content harmonisation flow after generating the keypoints.

        Args:
            keypoints: a list input of the keypoints from the articles to be compiled
        
        Returns:
            answer: a String containing the keypoints compiled by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
            ValueError: If there is <2 keypoints for comparison. This means there are no keypoints between articles to compile. 
        """
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
                answer = response['text']
                return answer
            else:
                return ValueError("There are insufficient number of keypoints to compare. Kindly add more articles to compare and try again.")
        else:
            raise TypeError(f"This node is a {self.role} node and cannot run compile_points()")

class Mistral(LLMInterface):
    """This class contains the methods for the Mistral class. It inherits from the LLMInterface abstract class.
        
        Attributes:
            model: a HuggingFaceEndpoint object for the specific model
            prompt_template: a LLMPrompt object for the specific model
            role: a String dictating the role of the llm

    """
    def __init__(self, model, prompt_template, role):
        """Initializes the instance based on model, prompt_template and role input.

        Args:
          model: determines the model, in this case it will be a Mistral model
          prompt_template: the specific prompt template for the model and its role
          role: determines the role of the model in the article harmonisation process
        """
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def generate_text(self, article : str):
        """ Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".
        
        Args:
            article: a String input of the article content
        
        Returns:
            answer: a String containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.

        """
        if self.role == "Researcher":
            prompt_t = PromptTemplate(input_variables=["Article"], template=self.prompt_template.return_researcher_prompt())
            chain = prompt_t | self.model | StrOutputParser()
            print("generating keypoints")
            response = chain.invoke(article)
            print("keypoints generated")
            return response
        else:
            raise TypeError(f"This node is a {self.role} node and cannot run generate_text()")
    
    def compile_points(self, keypoints: list = []):
        """ A list of keypoints from different articles are compiled using this method. This is the second step in the content harmonisation flow after generating the keypoints.

        Args:
            keypoints: a list input of the keypoints from the articles to be compiled
        
        Returns:
            answer: a String containing the keypoints compiled by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
            ValueError: If there is <2 keypoints for comparison. This means there are no keypoints between articles to compile. 
        """
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
                return ValueError("There are insufficient number of keypoints to compare. Kindly add more articles to compare and try again.")
        else:
            raise TypeError(f"This node is a {self.role} node and cannot run compile_points()")
