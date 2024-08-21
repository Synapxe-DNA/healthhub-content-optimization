import re
from abc import ABC, abstractmethod
from operator import itemgetter

from config import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import AzureChatOpenAI

from .enums import MODELS, ROLES
from .prompts import prompt_tool

MAX_NEW_TOKENS = settings.MAX_NEW_TOKENS
AZURE_COGNITIVE_SERVICES = settings.AZURE_COGNITIVE_SERVICES
AZURE_OPENAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_VERSION = settings.AZURE_OPENAI_API_VERSION
AZURE_AD_TOKEN_PROVIDER = settings.AZURE_AD_TOKEN_PROVIDER


def start_llm(model: str, role: str, temperature: int = 0):
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
    model = model.lower()

    match model:
        case "llama3":
            # creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model)
            # starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS.llama3.value, max_new_tokens=MAX_NEW_TOKENS
            )
            return HuggingFace(llm, model_prompter, role)

        case "mistral":
            # creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model=model)
            # starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS.mistral.value, max_new_tokens=MAX_NEW_TOKENS
            )
            return HuggingFace(llm, model_prompter, role)

        case "azure":
            model_prompter = prompt_tool(model=model)
            llm = AzureChatOpenAI(
                azure_ad_token_provider=AZURE_AD_TOKEN_PROVIDER,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                cache=None,
                callbacks=None,
                custom_get_token_ids=None,
                azure_deployment=MODELS.azure.value,
                frequency_penalty=0,
                logprobs=None,
                max_retries=2,
                max_tokens=MAX_NEW_TOKENS,
                n=1,
                api_version=AZURE_OPENAI_API_VERSION,
                timeout=None,
                seed=42,
                streaming=False,
                temperature=temperature,
                top_p=1,
                verbose=True,
            )
            return Azure(llm, model_prompter, role)

        case _:
            raise ValueError(
                f"You have entered {model}, which is not a supported model type"
            )


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
    def evaluate_title(self, title: str, content: str) -> str:
        """
        Abstract method for generating the text of the LLM Model

        Args:
            title: a String input stating the article title
            content: a String input stating the article content

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
        if self.role != ROLES.RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=self.prompt_template.return_researcher_prompt(),
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke(article)
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
        if self.role != ROLES.COMPILER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run compile_points()"
            )

        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_compiler_prompt()
        )

        input_keypoints = ""
        for article_index in range(len(keypoints)):
            article_kp = keypoints[article_index]
            input_keypoints += f"""
                ### Start of Article {article_index + 1} Keypoints ###
                {article_kp}
                ### End of Article {article_index + 1} Keypoints ###
                """

        chain = prompt_t | self.model
        print("Compiling keypoints for article harmonisation")
        res = chain.invoke({"Keypoints": input_keypoints})
        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints: list = []):
        if self.role != ROLES.CONTENT_OPTIMISATION:
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
        if self.role != ROLES.WRITING_OPTIMISATION:
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

    def optimise_title(self, content):
        if self.role != ROLES.TITLE:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_title()"
            )
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_title_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article title")
        response = chain.invoke({"Content": content})
        print("Article title optimised")
        return response

    def optimise_meta_desc(self, content):
        if self.role != ROLES.META_DESC:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_meta_desc()"
            )
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_meta_desc_prompt()
        )

        chain = prompt_t | self.model
        print("Optimising article meta description")
        response = chain.invoke({"Content": content})
        print("Article meta description optimised")
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

        prompt_t = ChatPromptTemplate.from_messages(template)

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_title(self, title: str, content: str) -> str:

        template = self.prompt_template.return_title_evaluation_prompt()

        prompt_t = ChatPromptTemplate.from_messages(template)

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"title": title, "article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:

        template = self.prompt_template.return_meta_desc_evaluation_prompt()

        prompt_t = ChatPromptTemplate.from_messages(template)

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"meta": meta_description, "article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_personality(self, content: str) -> bool:

        template = self.prompt_template.return_personality_evaluation_prompt()

        prompt_t = ChatPromptTemplate.from_messages(template)

        chain = prompt_t | self.model | StrOutputParser()
        print("Evaluating personality of article")
        res = chain.invoke({"Content": content})
        print("Article personality evaluated")

        response = re.sub(" +", " ", res)

        if "True" in response:
            print("Article writing meets personality guidelines")
            return True
        else:
            print("Article writing does not meet personality guidelines")
            return False

    def generate_keypoints(self, article: str):
        """
        Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".

        Args:
            article: a String input of the article content

        Returns:
            answer: a String containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
        """
        if self.role != ROLES.RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_researcher_prompt("generate keypoints"),
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Article": article})
        response = re.sub(" +", " ", res)

        return response

    def add_additional_content(self, keypoints: str, additional_content: str):
        """
        Adds additional content form the user.

        Args:
            keypoints: a string input of the keypoints from the researcher node
            additional_content: a string input of the additional content ot be added to the article

        Returns:
            answer: a string containing the keypoints and additional content

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
        """
        # Raise an error if the role is not a compiler
        if self.role != ROLES.RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run add_additional_content()"
            )

        # Extracting the additional content prompt
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_researcher_prompt("add additional input")
        )

        # Declaring the chain
        chain = prompt_t | self.model | StrOutputParser()

        # Invoking the chain with the required inputs
        res = chain.invoke(
            {"additional_content": additional_content, "content": keypoints}
        )

        # Regex to remove white spaces
        response = re.sub(" +", " ", res)

        # Returning the response from the llm after regex
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
        if self.role != ROLES.COMPILER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run compile_points()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_compiler_prompt()
        )

        input_keypoints = ""
        for article_index in range(len(keypoints)):
            article_kp = keypoints[article_index]
            input_keypoints += f"""
            ### Start of Article {article_index + 1} Keypoints ###
            {article_kp}
            ### End of Article {article_index + 1} Keypoints ###
            """

        chain = prompt_t | self.model | StrOutputParser()
        print("Compiling keypoints for article harmonisation...")
        res = chain.invoke({"Keypoints": input_keypoints})

        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints):
        if self.role != ROLES.CONTENT_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article content based on content guidelines...")
        res = chain.invoke(
            {
                "Keypoints": keypoints,
            }
        )
        print("Article content optimised")
        response = re.sub(" +", " ", res)

        return response

    def optimise_writing(self, content: str):
        if self.role != ROLES.WRITING_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_writing_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article writing based on writing guidelines...")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response

    def optimise_readability(self, content: str, step: str):
        """Rewrites the content based on the fiven feedback"""
        if self.role != ROLES.READABILITY_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_readability()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_hemingway_readability_optimisation_prompt(step)
        )

        chain = prompt_t | self.model | StrOutputParser()
        print(f"-- {step} --")
        response = chain.invoke(
            {
                # "Readability_evaluation": readability_evaluation,
                "content": content
            }
        )
        return response

    def optimise_title(self, content, feedback):
        if self.role != ROLES.TITLE:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_title()"
            )
        optimise_title_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_prompt("optimise title")
        )

        shorten_title_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_prompt("shorten title")
        )

        optimise_title_chain = (
            optimise_title_prompt
            | self.model
            | StrOutputParser()
            | {"title": RunnablePassthrough()}
        )
        shorten_title_chain = shorten_title_prompt | self.model | StrOutputParser()
        chain = (
            optimise_title_chain
            | {"content": itemgetter("title")}
            | RunnableParallel(title=shorten_title_chain)
        )

        print("Optimising article title...")
        response = chain.invoke({"content": content, "feedback": feedback})
        print("Article title optimised")

        response = response["title"]

        return response

    def optimise_meta_desc(self, content, feedback):
        if self.role != ROLES.META_DESC:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_meta_desc()"
            )
        optimise_meta_desc_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_prompt("optimise meta desc")
        )

        shorten_meta_desc_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_prompt("shorten meta desc")
        )

        optimise_meta_desc_chain = (
            optimise_meta_desc_prompt
            | self.model
            | StrOutputParser()
            | {"meta_desc": RunnablePassthrough()}
        )
        shorten_meta_desc_chain = (
            shorten_meta_desc_prompt | self.model | StrOutputParser()
        )
        chain = (
            optimise_meta_desc_chain
            | {"content": itemgetter("meta_desc")}
            | RunnableParallel(meta_desc=shorten_meta_desc_chain)
        )
        print("Optimising article meta description...")
        response = chain.invoke({"content": content, "feedback": feedback})
        print("Article meta description optimised")
        response = response["meta_desc"]
        return response


if __name__ == "__main__":
    llm = start_llm(model="llama3", role="test")
    print(llm.invoke("How are you today?"))
