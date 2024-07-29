import os
import re
from abc import ABC, abstractmethod

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from prompts import prompt_tool

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

credential = DefaultAzureCredential()
AZURE_COGNITIVE_SERVICES = os.getenv("AZURE_COGNITIVE_SERVICES", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE", "")
AZURE_OPENAI_AD_TOKEN = credential.get_token(AZURE_COGNITIVE_SERVICES).token
os.environ["AZURE_OPENAI_API_TYPE"] = AZURE_OPENAI_API_TYPE
os.environ["AZURE_OPENAI_AD_TOKEN"] = AZURE_OPENAI_AD_TOKEN

MODELS = [
    # Meta Llama
    "meta-llama/Meta-Llama-3-8B-Instruct",
    # "meta-llama/Meta-Llama-3.1-8B-Instruct",
    # Phi 3
    "microsoft/Phi-3-mini-128k-instruct",
    # Mistral
    "mistralai/Mistral-7B-Instruct-v0.3",
    # "NousResearch/Hermes-2-Pro-Mistral-7B",
    # InternLM
    "internlm/internlm2_5-7b-chat",
]

MAX_NEW_TOKENS = 5000

# Declaring node roles
EVALUATOR = "Evaluator"
EXPLAINER = "Explainer"
RESEARCHER = "Researcher"
COMPILER = "Compiler"
META_DESC = "Meta description optimisation"
TITLE = "Title optimisation"
CONTENT_OPTIMISATION = "Content optimisation"
WRITING_OPTIMISATION = "Writing optimisation"


def start_llm(model: str, role: str):
    """
    Starts up and returns an instance of a specific model type

    Args:
        model: a String input stating the model used
        role: a String input stating the role of the model. List of model roles can be found under NODE_ROLES in harmonisation.py

    Returns:
        an object from the model class pertaining to the string input

    Raises:
        ValueError: if the input model is not supported, yet
    """

    match model.lower():
        case "llama3":
            # creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model)
            # starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS[0], max_new_tokens=MAX_NEW_TOKENS
            )
            return HuggingFace(llm, model_prompter, role)

        case "mistral":
            # creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model=model)
            # starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MISTRAL, max_new_tokens=MAX_NEW_TOKENS
            )
            return HuggingFace(llm, model_prompter, role)

        case "internlm":
            model_prompter = prompt_tool(model=model)
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS[3], max_new_tokens=MAX_NEW_TOKENS
            )
            return HuggingFace(llm, model_prompter, role)

        # TODO: Complete Azure OpenAI model class and setup
        # case "azure-openai":
        #     model_prompter = prompt_tool(model=model)
        #     llm = AzureOpenAI(
        #         api_version=AZURE_OPENAI_API_VERSION,
        #         model_name="gpt-3.5-turbo-instruct",
        #         azure_ad_token=AZURE_OPENAI_AD_TOKEN,
        #         max_tokens=MAX_NEW_TOKENS,
        #     )

        case _:
            raise ValueError(f"You entered {model}, which is not a support model type")


class LLMInterface(ABC):
    """
    Abstract class for all LLM classes. Each unique LLM model will have its own LLM class, which must inherit from this class, hence they must all include the following methods.

    This class inherits from ABC class.
    """

    @abstractmethod
    def evaluate_content(self, content: str, choice: str) -> str:
        """
        Abstract method for generating the text of the LLM Model

        Args:
            content: a String input stating the text
            choice: a String input stating the choice

        Returns:

        """
        pass

    @abstractmethod
    def evaluate_title(self, text: str) -> str:
        """
        Abstract method for generating the text of the LLM Model

        Args:
            text: a String input stating the text

        Returns:

        """
        pass

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:
        """
        Abstract method for generating the text of the LLM Model

        Args:
            meta_description: a String input stating the meta description
            content: a String input stating the text
        """
        pass

    @abstractmethod
    def generate_keypoints(self, article: str) -> str:
        """
        Abstract method for generating and returning a summary of keypoints based on the article

        Args:
            article: String input of the article to be summarised

        Returns:

        """
        pass

    @abstractmethod
    def compile_points(self, keypoints: list[str]) -> str:
        """
        Abstract method for compiling and returing from a list of keypoints

        Args:
            keypoints: list input of the article keypoints to be compiled

        Returns:

        """
        pass

    @abstractmethod
    def optimise_content(self, keypoints: list[str]) -> str:
        """
        Abstract method for generating the article content based on the article keypoints

        Args:
            keypoints: list of compiled keypoints

        Returns:

        """
        pass

    @abstractmethod
    def optimise_writing(self, content: str) -> str:
        """
        Abstract method for optimising the generated article content based on the writing guidelines

        Args:
            content: generated article content

        Returns:

        """
        pass

    @abstractmethod
    def optimise_content(self, keypoints):
        """Abstract method for optimising the content in the keypoints extracted from previous steps based on the content guidelines from the playbook.

        Args:
            keypoints: list input of the article keypoints to have their content optimised
        """
        pass

    @abstractmethod
    def optimise_writing(self, content):
        """Abstract method for optimising the writing in the optimised content from the previous based on the writing guidelines from the playbook.

        Args:
            content: string input of optimised content from the previous optimise_content_node
        """
        pass

    @abstractmethod
    def optimise_title(self, content):
        """Abstract method for optimising the article's title based on the article's keypoints or optimised writing

        Args:
            content: string input of article's optimised writing or extracted keypoints
        """
        pass

    @abstractmethod
    def optimise_meta_desc(self, content):
        """Abstract method for optimising the article's meta description based on the article's keypoints or optimised writing

        Args:
            content: string input of article's optimised writing or extracted keypoints
        """
        pass


class HuggingFace(LLMInterface):
    """
    This class contains the methods for the Llama3 class. It inherits from the LLMInterface abstract class.

    Attributes:
        model: a HuggingFaceEndpoint object for the specific model
        prompt_template: a LLMPrompt object for the specific model
        role: a String dictating the role of the llm
    """

    def __init__(self, model, prompt_template, role):
        """
        Initializes the instance based on model, prompt_template and role input.

        Args:
          model: determines the model, in this case it will be a Llama3 model.
          prompt_template: the specific prompt template for the model and its role.
          role: determines the role of the model in the article harmonisation process.
        """
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def evaluate_content(self, content: str, choice: str = "readability") -> str:

        match choice.lower():
            case "readability":
                template = self.prompt_template.return_readability_evaluation_prompt()
            case "structure":
                template = self.prompt_template.return_structure_evaluation_prompt()
            case _:
                raise ValueError(f"You entered {choice}, which is not a valid choice")

        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke(content)
        response = re.sub(" +", " ", res)

        return response

    def evaluate_title(self, title: str, content: str) -> str:

        template = self.prompt_template.return_title_evaluation_prompt()

        prompt_t = PromptTemplate(
            input_variables=["Title", "Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Title": title, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:

        template = self.prompt_template.return_meta_desc_evaluation_prompt()

        prompt_t = PromptTemplate(
            input_variables=["Meta", "Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Meta": meta_description, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def generate_keypoints(self, article: str, num: int):
        """
        Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".

        Args:
            article: a String input of the article content

        Returns:
            answer: a String containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
        """
        # Raise an error if the role is not a researcher
        if self.role != RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=self.prompt_template.return_researcher_prompt(),
        )

        chain = prompt_t | self.model | StrOutputParser()
        print(f"Processing keypoints for header {num}")
        res = chain.invoke(article)
        print(f"Keypoints processed for header {num}")
        response = re.sub(" +", " ", res)

        return response

    def compile_points(self, keypoints: list = []):
        """
        A list of keypoints from different articles are compiled using this method. This is the second step in the content harmonisation flow after generating the keypoints.

        Args:
            keypoints: a list input of the keypoints from the articles to be compiled

        Returns:
            answer: a String containing the keypoints compiled by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
            ValueError: If there is less than 2 keypoints for comparison. This means there are no keypoints between articles to compile.
        """
        # Raise an error if there is less than 2 keypoints
        if len(keypoints) < 2:
            raise ValueError(
                "There are insufficient keypoints to compare. Kindly add more articles to compare and try again."
            )

        # Raise an error if the role is not a compiler
        if self.role != COMPILER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run compile_points()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_compiler_prompt()
        )

        input_keypoints = ""
        for article_index in range(len(keypoints)):
            article_kp = keypoints[article_index]
            input_keypoints += (
                f"\n Article {article_index + 1} Keypoints:\n{article_kp}"
            )

        chain = prompt_t | self.model
        print("Compiling keypoints for article harmonisation")
        res = chain.invoke({"Keypoints": input_keypoints})
        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints: list = []):
        if self.role != CONTENT_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_content_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article content")
        res = chain.invoke({"Keypoints": keypoints})
        print("Article content optimised")
        response = re.sub(" +", " ", res)

        return response

    def optimise_writing(self, content):
        if self.role != WRITING_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_writing()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_writing_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article writing")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response


class Azure(LLMInterface):
    def __init__(self, model, prompt_template, role):
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def evaluate_content(self, content: str, choice: str = "readability") -> str:

        match choice.lower():
            case "readability":
                template = self.prompt_template.return_readability_evaluation_prompt()
            case "structure":
                template = self.prompt_template.return_structure_evaluation_prompt()
            case _:
                raise ValueError(f"You entered {choice}, which is not a valid choice")

        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke(content)
        response = re.sub(" +", " ", res)

        return response

    def evaluate_title(self, title: str, content: str) -> str:

        template = self.prompt_template.return_title_evaluation_prompt()

        prompt_t = PromptTemplate(
            input_variables=["Title", "Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Title": title, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:

        template = self.prompt_template.return_meta_desc_evaluation_prompt()

        prompt_t = PromptTemplate(
            input_variables=["Meta", "Article"],
            template=template,
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Meta": meta_description, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def generate_keypoints(self, article: str, num: int):
        """
        Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".

        Args:
            article: a String input of the article content

        Returns:
            answer: a String containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
        """
        # Raise an error if the role is not a researcher
        if self.role != RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=self.prompt_template.return_researcher_prompt(),
        )

        chain = prompt_t | self.model | StrOutputParser()
        print(f"Processing keypoints for header {num}")
        res = chain.invoke(article)
        print(f"Keypoints processed for header {num}")
        response = re.sub(" +", " ", res)

        return response

    def compile_points(self, keypoints: list = []):
        """
        A list of keypoints from different articles are compiled using this method. This is the second step in the content harmonisation flow after generating the keypoints.

        Args:
            keypoints: a list input of the keypoints from the articles to be compiled

        Returns:
            answer: a String containing the keypoints compiled by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
            ValueError: If there is less than 2 keypoints for comparison. This means there are no keypoints between articles to compile.
        """
        # Raise an error if there is less than 2 keypoints
        if len(keypoints) < 2:
            raise ValueError(
                "There are insufficient keypoints to compare. Kindly add more articles to compare and try again."
            )

        # Raise an error if the role is not a compiler
        if self.role != COMPILER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run compile_points()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_compiler_prompt()
        )

        input_keypoints = ""
        for article_index in range(len(keypoints)):
            article_kp = keypoints[article_index]
            input_keypoints += (
                f"\n Article {article_index + 1} Keypoints:\n{article_kp}"
            )

        chain = prompt_t | self.model
        print("Compiling keypoints for article harmonisation")
        res = chain.invoke({"Keypoints": input_keypoints})
        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints: list = []):
        if self.role != CONTENT_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_content_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article content")
        res = chain.invoke({"Keypoints": keypoints})
        print("Article content optimised")
        response = re.sub(" +", " ", res)

        return response

    def optimise_writing(self, content: str):
        if self.role != WRITING_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_writing_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article writing")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response
