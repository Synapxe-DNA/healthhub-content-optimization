import re
from abc import ABC, abstractmethod
from operator import itemgetter

from config import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import AzureChatOpenAI
from utils.formatters import parse_string_to_boolean

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
        model (str): a String input stating the model used. List of models can be found in enums.py
        role (str): a String input stating the role of the model. List of agentic roles can be found in enums.py
        temperature (int): an Integer input stating the temperature of the model. It influences the probability distribution of the next word
    Returns:
        an object from the model class pertaining to the string input

    Raises:
        ValueError: if the input model is not supported, yet
    """
    model = model.lower()

    match model:
        case "llama3":
            # Creating an instance of a LLMPrompt object based on the Llama 3 model
            model_prompter = prompt_tool(model)
            # Starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS.LLAMA3.value, max_new_tokens=MAX_NEW_TOKENS, temperature=temperature
            )
            return HuggingFace(llm, model_prompter, role)

        case "mistral":
            # Creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model=model)
            # Starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS.MISTRAL.value, max_new_tokens=MAX_NEW_TOKENS, temperature=temperature
            )
            return HuggingFace(llm, model_prompter, role)

        case "azure":
            # Creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model=model)
            # Starting an instance of the model using Azure OpenAI
            llm = AzureChatOpenAI(
                azure_ad_token_provider=AZURE_AD_TOKEN_PROVIDER,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                cache=None,
                callbacks=None,
                custom_get_token_ids=None,
                azure_deployment=MODELS.AZURE.value,
                frequency_penalty=0,
                logprobs=None,
                max_retries=2,
                max_tokens=MAX_NEW_TOKENS,
                n=1,
                api_version=AZURE_OPENAI_API_VERSION,
                # timeout=240,  # Added request timeout of 240 seconds
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
    def evaluate_content(self, content: str, choice: str):
        """
        Abstract method for generating the text of the LLM Model

        Args:
            content (str): a String input stating the text
            choice (str): a String input stating the choice
        """
        pass

    @abstractmethod
    def evaluate_title(self, title: str, content: str):
        """
        Abstract method for generating the text of the LLM Model

        Args:
            title (str): a String input stating the article title
            content (str): a String input stating the article content
        """
        pass

    def evaluate_meta_description(self, meta_description: str, content: str):
        """
        Abstract method for generating the text of the LLM Model

        Args:
            meta_description (str): a String input stating the meta description
            content (str): a String input stating the text
        """
        pass

    @abstractmethod
    def generate_keypoints(self, article: str):
        """
        Abstract method for generating and returning a summary of keypoints based on the article

        Args:
            article (str): String input of the article to be summarised
        """
        pass

    @abstractmethod
    def compile_points(self, keypoints: list[str]):
        """
        Abstract method for compiling and returning from a list of keypoints

        Args:
            keypoints (list[str]): list input of the article keypoints to be compiled
        """
        pass

    @abstractmethod
    def optimise_content(self, keypoints: list[str]):
        """
        Abstract method for generating the article content based on the article keypoints

        Args:
            keypoints (list[str]): list of compiled keypoints
        """
        pass

    @abstractmethod
    def optimise_writing(self, content: str):
        """
        Abstract method for optimising the generated article content based on the writing guidelines

        Args:
            content (str): generated article content
        """
        pass

    @abstractmethod
    def optimise_title(self, content: str):
        """
        Abstract method for optimising the article's title based on the article's keypoints or optimised writing

        Args:
            content (str): optimised article content
        """
        pass

    @abstractmethod
    def optimise_meta_desc(self, content: str):
        """
        Abstract method for optimising the article's meta description based on the article's keypoints or optimised writing

        Args:
            content (str): optimised article content
        """
        pass


class HuggingFace(LLMInterface):
    """
    This class contains the methods for the HuggingFace models. It inherits from the LLMInterface abstract class.

    Attributes:
        model: a HuggingFaceEndpoint object for the specific model
        prompt_template: a LLMPrompt object for the specific model
        role: a String dictating the role of the llm
    """

    def __init__(self, model, prompt_template, role):
        """
        Initializes the instance based on model, prompt_template and role input.

        Args:
          model: determines the model, in this case it will be derived from the HuggingFaceEndpoint class.
          prompt_template: the specific prompt template for the model and its role.
          role: determines the role of the model in the article harmonisation process.
        """
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def evaluate_content(self, content: str, choice: str = "readability") -> str:
        """
        Perform Article Content Evaluation either on readability or content structure (writing style)

        This method analyzes the given content using one of two evaluation modes: 'readability' for assessing how easy
        the content is to read, or 'structure' for evaluating the quality and organization of the content's writing style.

        Args:
            content (str): The article content to be evaluated.
            choice (str): The evaluation mode. Should be either "readability" to assess readability or "structure"
                to evaluate the writing style. Defaults to "readability".

        Returns:
            str: A response string containing the evaluation results for the provided content.

        Raises:
            ValueError: If the choice provided is not "readability" or "structure".
        """

        # Fetch prompt from prompts.py
        match choice.lower():
            case "readability":
                template = self.prompt_template.return_readability_evaluation_prompt()
            case "structure":
                template = self.prompt_template.return_structure_evaluation_prompt()
            case _:
                raise ValueError(f"You entered {choice}, which is not a valid choice")

        # Define the prompt template and inputs
        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=template,
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke(content)
        response = re.sub(" +", " ", res)

        return response

    def evaluate_title(self, title: str, content: str) -> str:
        """
        Perform Article Title Evaluation by determining the relevance of the article title with respect to its content

        Args:
            title (str): The article title to be evaluated.
            content (str): The article content to be evaluated.

        Returns:
            str: A response string containing the evaluation results for the provided title.
        """

        # Fetch prompt from prompts.py
        template = self.prompt_template.return_title_evaluation_prompt()

        # Define the prompt template and inputs
        prompt_t = PromptTemplate(
            input_variables=["Title", "Article"],
            template=template,
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Title": title, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:
        """
        Perform Article Meta Description Evaluation by determining the relevance of the article meta description with
        respect to its content

        Args:
            meta_description (str): The article meta description to be evaluated.
            content (str): The article content to be evaluated.

        Returns:
            str: A response string containing the evaluation results for the provided meta description.
        """

        # Fetch prompt from prompts.py
        template = self.prompt_template.return_meta_desc_evaluation_prompt()

        # Define the prompt template and inputs
        prompt_t = PromptTemplate(
            input_variables=["Meta", "Article"],
            template=template,
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Meta": meta_description, "Article": content})
        response = re.sub(" +", " ", res)

        return response

    def generate_keypoints(self, article: str):
        """
        Organises the sentences in an article into keypoints as decided by the LLM. All meaningful sentences will be placed
        under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".

        Args:
            article (str): a String input of the article content

        Returns:
            str: A response string containing the keypoints as determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts
            for each node is specific its role.
        """

        # Raise an error if the role is not a researcher
        if self.role != ROLES.RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        # Fetch prompt from prompts.py
        template = self.prompt_template.return_researcher_prompt()

        # Define the prompt template and inputs
        prompt_t = PromptTemplate(
            input_variables=["Article"],
            template=template,
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke(article)
        response = re.sub(" +", " ", res)

        return response

    def compile_points(self, keypoints: list = []):
        """
        A list of keypoints from different articles are compiled using this method. This is the second step in the content
        harmonisation flow after generating the keypoints.

        Args:
            keypoints (list[str]): a list input of the keypoints from the articles to be compiled

        Returns:
            str: A response string containing the keypoints compiled by the LLM

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

        # Define the prompt template and inputs
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_compiler_prompt()
        )

        # Concatenate list of keypoints into a single string
        input_keypoints = ""
        for article_index in range(len(keypoints)):
            article_kp = keypoints[article_index]
            input_keypoints += f"""
                ### Start of Article {article_index + 1} Keypoints ###
                {article_kp}
                ### End of Article {article_index + 1} Keypoints ###
                """

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Compiling keypoints for article harmonisation")
        res = chain.invoke({"Keypoints": input_keypoints})
        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints: list = []):
        """
        An article is generated based on the keypoints provided.

        Args:
            keypoints (list[str]): a list input of the keypoints from the articles to be optimized

        Returns:
            str: A response string containing the generated article content

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raise an error if the role is not "Content optimisation"
        if self.role != ROLES.CONTENT_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        # Define the prompt template and inputs
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_content_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article content")
        res = chain.invoke({"Keypoints": keypoints})
        print("Article content optimised")
        response = re.sub(" +", " ", res)

        return response

    def optimise_writing(self, content):
        """
        The article is optimised as per the writing style guidelines

        Args:
            content (str): the article content

        Returns:
            str: A response string containing the optimised article content

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raises an error if the role is not "Writing optimisation"
        if self.role != ROLES.WRITING_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_writing()"
            )

        # Define the prompt template and inputs
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_writing_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article writing")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response

    def optimise_title(self, content):
        """
        The article title is generated based on the optimised article content

        Args:
            content (str): the optimised article content

        Returns:
              str: A response string containing the optimised article title

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raises an error if the role is not "Title optimisation"
        if self.role != ROLES.TITLE:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_title()"
            )

        # Define the prompt template and inputs
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_title_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article title")
        response = chain.invoke({"Content": content})
        print("Article title optimised")

        return response

    def optimise_meta_desc(self, content):
        """
        The article meta description is generated based on the optimised article content

        Args:
            content (str): the optimised article content

        Returns:
            str: A response string containing the optimised article meta description

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raises an error if the role is not "Meta description optimisation"
        if self.role != ROLES.META_DESC:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_meta_desc()"
            )

        # Define the prompt template and inputs
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_meta_desc_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article meta description")
        response = chain.invoke({"Content": content})
        print("Article meta description optimised")

        return response


class Azure(LLMInterface):
    """
    
    """
    def __init__(self, model, prompt_template, role):
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def evaluation_summary_router(self, info):
        summarization_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_summarization_prompt()
        )
        summarization_chain = summarization_prompt | self.model | StrOutputParser()

        decision = info.get("decision")
        if decision:
            explanation = summarization_chain.invoke({"text": info.get("text")})
            return {"decision": decision, "explanation": explanation}
        else:
            return {"decision": decision, "explanation": None}

    def evaluate_content(self, content: str, choice: str = "readability") -> str:

        match choice.lower():
            case "readability":
                evaluation_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_readability_evaluation_prompt()
                )
                summarization_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_summarization_prompt()
                )

                evaluation_chain = (
                    evaluation_prompt
                    | self.model
                    | StrOutputParser()
                    | {"evaluation": RunnablePassthrough()}
                )
                summarization_chain = (
                    summarization_prompt | self.model | StrOutputParser()
                )

                chain = (
                    evaluation_chain
                    | {"text": itemgetter("evaluation")}
                    | {
                        "explanation": summarization_chain,
                    }
                )

            case "structure":
                evaluation_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_structure_evaluation_prompt()
                )
                decision_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_decision_prompt()
                )

                evaluation_chain = (
                    evaluation_prompt
                    | self.model
                    | StrOutputParser()
                    | {"evaluation": RunnablePassthrough()}
                )
                decision_chain = (
                    decision_prompt
                    | self.model
                    | StrOutputParser()
                    | RunnableLambda(parse_string_to_boolean)
                )

                chain = (
                    evaluation_chain
                    | {"text": itemgetter("evaluation")}
                    | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
                    | RunnableLambda(self.evaluation_summary_router)
                )

            case _:
                raise ValueError(f"You entered {choice}, which is not a valid choice")

        # print(chain.get_graph().print_ascii())

        print(f"Evaluating content {choice}")
        res = chain.invoke({"article": content})
        print(f"Content {choice} evaluated")

        return res

    def evaluate_title(self, title: str, content: str) -> str:
        evaluation_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_evaluation_prompt()
        )
        decision_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_decision_prompt()
        )

        evaluation_chain = (
            evaluation_prompt
            | self.model
            | StrOutputParser()
            | {"evaluation": RunnablePassthrough()}
        )
        decision_chain = (
            decision_prompt
            | self.model
            | StrOutputParser()
            | RunnableLambda(parse_string_to_boolean)
        )

        chain = (
            evaluation_chain
            | {"text": itemgetter("evaluation")}
            | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
            | RunnableLambda(self.evaluation_summary_router)
        )

        # print(chain.get_graph().print_ascii())

        print("Evaluating title")
        res = chain.invoke({"title": title, "article": content})
        print("Title evaluated")

        return res

    def evaluate_meta_description(self, meta_description: str, content: str) -> str:
        evaluation_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_evaluation_prompt()
        )
        decision_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_decision_prompt()
        )

        evaluation_chain = (
            evaluation_prompt
            | self.model
            | StrOutputParser()
            | {"evaluation": RunnablePassthrough()}
        )
        decision_chain = (
            decision_prompt
            | self.model
            | StrOutputParser()
            | RunnableLambda(parse_string_to_boolean)
        )

        chain = (
            evaluation_chain
            | {"text": itemgetter("evaluation")}
            | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
            | RunnableLambda(self.evaluation_summary_router)
        )

        # print(chain.get_graph().print_ascii())

        print("Evaluating meta description")
        res = chain.invoke({"meta": meta_description, "article": content})
        print("Meta description evaluated")

        return res

    def evaluate_personality(self, content: str) -> bool:

        template = self.prompt_template.return_personality_evaluation_prompt()

        prompt_t = ChatPromptTemplate.from_messages(template)

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Content": content})
        response = re.sub(" +", " ", res)

        if "True" in response:
            return True
        else:
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
            self.prompt_template.return_researcher_prompt(),
        )

        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Article": article})
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
        print("Compiling keypoints for article harmonisation")
        res = chain.invoke({"Keypoints": input_keypoints})

        print("Keypoints compiled for article harmonisation")
        response = re.sub(" +", " ", res)

        return response

    def optimise_content(self, keypoints, structure_evaluation: str):
        if self.role != ROLES.CONTENT_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_content()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article content")
        res = chain.invoke(
            {"Keypoints": keypoints, "Structure_evaluation": structure_evaluation}
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
        print("Optimising article writing")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response

    def optimise_readability(self, content: str, readability_evaluation: str):
        """Rewrites the content based on the fiven feedback"""
        if self.role != ROLES.READABILITY_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_readability()"
            )
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_readability_optimisation_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("-- Optimising article readability --")
        response = chain.invoke(
            {"Readability_evaluation": readability_evaluation, "Content": content}
        )
        print("-- Article readability optimised --")
        return response

    def optimise_title(self, content):
        if self.role != ROLES.TITLE:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_title()"
            )
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article title")
        response = chain.invoke({"Content": content})
        print("Article title optimised")
        return response

    def optimise_meta_desc(self, content):
        if self.role != ROLES.META_DESC:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_meta_desc()"
            )
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article meta description")
        response = chain.invoke({"Content": content})
        print("Article meta description optimised")
        return response
