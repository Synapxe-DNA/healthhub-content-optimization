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
                endpoint_url=MODELS.LLAMA3.value,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=temperature,
            )
            return HuggingFace(llm, model_prompter, role)

        case "mistral":
            # Creating an instance of a LLMPrompt object based on the model used
            model_prompter = prompt_tool(model=model)
            # Starting an instance of the model using HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                endpoint_url=MODELS.MISTRAL.value,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=temperature,
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

    @abstractmethod
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

    # @abstractmethod
    # def optimise_content(self, keypoints: list[str]):
    #     """
    #     Abstract method for generating the article content based on the article keypoints

    #     Args:
    #         keypoints (list[str]): list of compiled keypoints
    #     """
    #     pass

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

        # Define the prompt template
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

        # Define the prompt template
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

    def optimise_writing(self, content: str):
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

        # Define the prompt template
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_writing_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article writing")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response

    def optimise_title(self, content: str):
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

        # Define the prompt template
        prompt_t = PromptTemplate.from_template(
            self.prompt_template.return_title_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model
        print("Optimising article title")
        response = chain.invoke({"Content": content})
        print("Article title optimised")

        return response

    def optimise_meta_desc(self, content: str):
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

        # Define the prompt template
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
    This class contains the methods for the Azure OpenAI models. It inherits from the LLMInterface abstract class.

    Attributes:
        model: an AzureChatOpenAI object for the specific model
        prompt_template: a LLMPrompt object for the specific model
        role: a String dictating the role of the llm
    """

    def __init__(self, model, prompt_template, role):
        """
        Initializes the instance based on model, prompt_template and role input.

        Args:
          model: determines the model, in this case it will be derived from the AzureChatOpenAI class.
          prompt_template: the specific prompt template for the model and its role.
          role: determines the role of the model in the article harmonisation process.
        """
        self.model = model
        self.prompt_template = prompt_template
        self.role = role

    def evaluation_summary_router(self, evaluation: dict) -> dict:
        """
        Routes the evaluation result and generates a summary if a decision (True/False) is present.

        This method takes an evaluation dictionary and processes it based on whether a decision is present. If a decision
        is True, it generates a summary explanation using a LLM. Otherwise, it returns the decision without an explanation.

        Args:
            evaluation (dict): A dictionary containing the evaluation results. Expected to have 'decision' and 'text' keys.

        Returns:
            dict: A dictionary containing:
                  - 'decision': The original decision from the evaluation.
                  - 'explanation': A summarized explanation if the decision is True, otherwise None.
        """

        # Create a summarization chain using the prompt template and language model
        summarization_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_summarization_prompt()
        )
        summarization_chain = summarization_prompt | self.model | StrOutputParser()

        # Extract the decision from the evaluation dictionary
        decision = evaluation.get("decision")
        if decision:
            # If a decision is True, generate a summary explanation
            explanation = summarization_chain.invoke({"text": evaluation.get("text")})
            return {"decision": decision, "explanation": explanation}
        else:
            # If decision is False, return without an explanation
            return {"decision": decision, "explanation": None}

    def evaluate_content(self, content: str, choice: str = "readability") -> dict:
        """
        Evaluates the given content based on the specified choice - readability or structure (aka writing style).

        This method sets up and executes different evaluation chains depending on the choice parameter. It can evaluate
        content for readability or structure.

        Args:
            content (str): The article content to be evaluated.
            choice (str): The type of evaluation to perform. Options are "readability" (default) or "structure".

        Returns:
            dict: A dictionary containing:
                  - 'decision' (Optional[bool]): The decision from the evaluation (not included if choice is "readability").
                  - 'explanation': A summarized explanation if the decision is True, otherwise None.

        Raises:
            ValueError: If an invalid choice is provided.
        """

        match choice.lower():
            case "readability":
                # Set up prompts for readability evaluation and summarization
                evaluation_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_readability_evaluation_prompt()
                )
                summarization_prompt = ChatPromptTemplate.from_messages(
                    self.prompt_template.return_summarization_prompt()
                )

                # Create evaluation chain
                evaluation_chain = (
                    evaluation_prompt
                    | self.model
                    | StrOutputParser()
                    | {"evaluation": RunnablePassthrough()}
                )

                # Create summarization chain
                summarization_chain = (
                    summarization_prompt | self.model | StrOutputParser()
                )

                # Combine chains for readability evaluation
                chain = (
                    evaluation_chain
                    | {"text": itemgetter("evaluation")}
                    | {
                        "explanation": summarization_chain,
                    }
                )

            # # NOTE: Code is commented out as the Writing Style Evaluation is no longer required at the moment
            # case "structure":
            #     # Set up prompts for structure evaluation and decision-making
            #     evaluation_prompt = ChatPromptTemplate.from_messages(
            #         self.prompt_template.return_structure_evaluation_prompt()
            #     )
            #     decision_prompt = ChatPromptTemplate.from_messages(
            #         self.prompt_template.return_decision_prompt()
            #     )
            #
            #     # Create evaluation chain
            #     evaluation_chain = (
            #         evaluation_prompt
            #         | self.model
            #         | StrOutputParser()
            #         | {"evaluation": RunnablePassthrough()}
            #     )
            #
            #     # Create decision chain
            #     decision_chain = (
            #         decision_prompt
            #         | self.model
            #         | StrOutputParser()
            #         | RunnableLambda(parse_string_to_boolean)
            #     )
            #
            #     # Combine chains for structure evaluation
            #     chain = (
            #         evaluation_chain
            #         | {"text": itemgetter("evaluation")}
            #         | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
            #         | RunnableLambda(self.evaluation_summary_router)
            #     )

            case _:
                # Raise an error for invalid choices
                raise ValueError(f"You entered {choice}, which is not a valid choice")

        # # Print the flow of the chain object
        # print(chain.get_graph().print_ascii())

        # Execute the chain
        print(f"Evaluating content {choice}")
        res = chain.invoke({"article": content})
        print(f"Content {choice} evaluated")

        return res

    def evaluate_title(self, title: str, content: str, step: str) -> dict:
        """
        Evaluates the given article title based on its article content.

        Args:
            title (str): The article title to be evaluated.
            content (str): The article content to evaluate the article title.

        Returns:
            dict: A dictionary containing:
                  - 'decision': The decision from the evaluation.
                  - 'explanation': A summarized explanation if the decision is True, otherwise None.
        """

        # Set up prompts for title evaluation and decision-making
        evaluation_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_evaluation_prompt(step)
        )
        decision_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_decision_prompt()
        )

        # Create evaluation chain
        evaluation_chain = (
            evaluation_prompt
            | self.model
            | StrOutputParser()
            | {"evaluation": RunnablePassthrough()}
        )

        # Create decision chain
        decision_chain = (
            decision_prompt
            | self.model
            | StrOutputParser()
            | RunnableLambda(parse_string_to_boolean)
        )

        # Combine chains for title evaluation
        chain = (
            evaluation_chain
            | {"text": itemgetter("evaluation")}
            | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
            | RunnableLambda(self.evaluation_summary_router)
        )

        # # Print the flow of the chain object
        # print(chain.get_graph().print_ascii())

        # Execute the chain
        print("Evaluating title")
        res = chain.invoke({"title": title, "article": content})
        print("Title evaluated")

        return res

    def evaluate_meta_description(self, meta_description: str, content: str) -> dict:
        """
        Evaluates the given article meta description based on its article content.

        Args:
            meta_description (str): The article meta description to be evaluated.
            content (str): The article content to evaluate the article meta description.

        Returns:
            dict: A dictionary containing:
                  - 'decision': The decision from the evaluation.
                  - 'explanation': A summarized explanation if the decision is True, otherwise None.
        """

        # Set up prompts for title evaluation and decision-making
        evaluation_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_evaluation_prompt()
        )
        decision_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_decision_prompt()
        )

        # Create evaluation chain
        evaluation_chain = (
            evaluation_prompt
            | self.model
            | StrOutputParser()
            | {"evaluation": RunnablePassthrough()}
        )

        # Create decision chain
        decision_chain = (
            decision_prompt
            | self.model
            | StrOutputParser()
            | RunnableLambda(parse_string_to_boolean)
        )

        # Combine chains for title evaluation
        chain = (
            evaluation_chain
            | {"text": itemgetter("evaluation")}
            | RunnableParallel(text=itemgetter("text"), decision=decision_chain)
            | RunnableLambda(self.evaluation_summary_router)
        )

        # # Print the flow of the chain object
        # print(chain.get_graph().print_ascii())

        # Execute the chain
        print("Evaluating meta description")
        res = chain.invoke({"meta": meta_description, "article": content})
        print("Meta description evaluated")

        return res

    def evaluate_personality(self, content: str) -> bool:
        """
        Evaluates the given article personality/writing style based on its article content.

        Args:
            content (str): The article content to evaluate the article personality.

        Returns:
              bool: A boolean indicating whether the article content adheres to the writing guidelines

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raise an error if the role is not "Personality evaluation"
        if self.role != ROLES.PERSONALITY_EVALUATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run evaluate_personality()"
            )

        # Define the prompt template
        template = self.prompt_template.return_personality_evaluation_prompt()
        prompt_t = ChatPromptTemplate.from_messages(template)

        # Define the chain and execute it
        chain = (
            prompt_t
            | self.model
            | StrOutputParser()
            | RunnableLambda(parse_string_to_boolean)
        )
        print("Evaluating personality of article")
        response = chain.invoke({"Content": content})
        print("Article personality evaluated")

        return response

    def generate_keypoints(self, article: str) -> str:
        """
        Organises the sentences in an article into keypoints decided by the LLM. All meaningful sentences will be placed
        under a keypoint while meaningless sentences will be placed at the end under "Omitted sentences".

        Args:
            article (str): The article content from which the keypoints will be extracted.

        Returns:
            str: A response string containing the keypoints determined by the LLM

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function. This is because the prompts for each node is specific its role.
        """

        # Raise an error if the role is not "Researcher"
        if self.role != ROLES.RESEARCHER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run generate_keypoints()"
            )

        # Define the prompt template
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_researcher_prompt("generate keypoints"),
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        res = chain.invoke({"Article": article})

        # Regex to remove white spaces
        response = re.sub(" +", " ", res)

        return response

    def add_additional_content(self, keypoints: str, additional_content: str):
        """
        Adds additional content from the User Annotation Excel file.

        Args:
            keypoints(str): a string input of the keypoints from the researcher node
            additional_content(str): a string input of the additional content ot be added to the article

        Returns:
            str: a String containing the keypoints and additional content

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

        # Raise an error if the role is not "Compiler"
        if self.role != ROLES.COMPILER:
            raise TypeError(
                f"This node is a {self.role} node and cannot run compile_points()"
            )

        # Define the prompt template
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_compiler_prompt()
        )

        input_keypoints = ""
        # For loop that concatenates all keypoints into a single string with appropriate headers and footnotes
        for article_index in range(len(keypoints)):
            # Extracting the article keypoints from the keypoints list.
            article_kp = keypoints[article_index]

            # Concatenating the keypoints to input_keypoints with clear headers and ending
            input_keypoints += f"""
            ### Start of Article {article_index + 1} Keypoints ###
            {article_kp}
            ### End of Article {article_index + 1} Keypoints ###
            """

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        print("Compiling keypoints for article harmonisation...")
        res = chain.invoke({"Keypoints": input_keypoints})
        print("Keypoints compiled for article harmonisation")

        # Regex to remove white spaces
        response = re.sub(" +", " ", res)

        return response

    def optimise_healthy_content(
        self, keypoints: list[str], main_article_content: str = ""
    ) -> str:
        """
        A live healthy article is generated based on the keypoints provided.

        Args:
            keypoints (list[str]): a list input of the keypoints from the articles to be optimized
            main_article_content (str): a string input containing the article content for the main article

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

        print(
            "Optimising live healthy article content based on main article structure..."
        )

        # Define the prompt template for extracting article structure
        article_structure_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt(
                "extract main live healthy article structure"
            )
        )

        # Define the extract structure chain
        article_structure_chain = (
            article_structure_prompt | self.model | StrOutputParser()
        )

        article_structure = article_structure_chain.invoke(
            {"article": main_article_content}
        )

        # Define the prompt template for sorting article based on structure
        sorting_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt("structure live healthy")
        )

        # Define the sort article chain
        sort_article_chain = sorting_prompt | self.model | StrOutputParser()

        sorted_article = sort_article_chain.invoke(
            {"Structure": article_structure, "Keypoints": keypoints}
        )

        # Define the prompt template for optimising article content
        optimise_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt("optimise health and conditions")
        )

        # Define the optimise article chain
        optimise_article_chain = optimise_prompt | self.model | StrOutputParser()

        optimised_article = optimise_article_chain.invoke(
            {"sorted_content": sorted_article}
        )

        print("Article content optimised")

        # Regex to remove whitespaces
        response = re.sub(" +", " ", optimised_article)

        return response

    def optimise_disease_content(
        self,
        keypoints: list[str],
    ) -> str:
        """
        An disease and conditions article is generated based on the keypoints provided.
        This is a two step process: sort based on structure -> rewrite content

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

        # Define the prompt template for sorting health and conditions articles based on structure
        structure_health_conditions_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt(
                "structure health and conditions"
            )
        )

        # Define the sort article chain
        sort_article_chain = (
            structure_health_conditions_prompt
            | self.model
            | StrOutputParser()
            | {"sorted_content": RunnablePassthrough()}
        )

        # Define the prompt template for optimising health and conditions articles based on guidelines
        optimise_health_conditions_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_content_prompt("optimise health and conditions")
        )
        # Define the optimize article chain
        optimise_artice_chain = (
            optimise_health_conditions_prompt | self.model | StrOutputParser()
        )

        # Define the overall chain which first runs the sort chain and then the optimize chain
        # TODO: fix if broken
        chain = (
            sort_article_chain
            | {"sorted_content": itemgetter("sorted_content")}
            | RunnableParallel(content=optimise_artice_chain)
        )

        print("Optimizing disease and conditions article content...")
        res = chain.invoke(
            {
                "Keypoints": keypoints,
            }
        )
        print("Disease and condition article content optimised")

        # Regex to remove whitespaces
        response = res["content"]
        response = re.sub(" +", " ", response)

        return response

    def optimise_writing(self, content: str) -> str:
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

        # Define the prompt template
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_writing_prompt()
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        print("Optimising article writing based on writing guidelines...")
        response = chain.invoke({"Content": content})
        print("Article writing optimised")

        return response

    def optimise_readability(self, content: str, step: str) -> str:
        """
        Rewrites the article content based on the given readability evaluation. The objective is to improve article readability.

        Args:
            content (str): the article content for readability optimisation.
            step (str): Indicates the prompt of the readability optimisation step to use.

        Returns:
            str: A response string containing the optimized article content
        """

        # Raises an error if the role is not "Readability optimisation"
        if self.role != ROLES.READABILITY_OPTIMISATION:
            raise TypeError(
                f"This node is a {self.role} node and cannot run optimise_readability()"
            )

        # Define the prompt template
        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_hemingway_readability_optimisation_prompt(step)
        )

        # Define the chain and execute it
        chain = prompt_t | self.model | StrOutputParser()
        print(f"-- {step} --")
        response = chain.invoke(
            {
                # "Readability_evaluation": readability_evaluation,
                "content": content
            }
        )

        return response

    def get_xml(self, optimised_content):
        """
        Produces a XML version of the optimised article.

        Args:
            optimised_content (str): the optimised article content

        Returns:
            str: A response string containing the XML output.

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """
        # Raises an error if the role is not "Writing postprocessor"
        if self.role != ROLES.WRITING_POSTPROCESSOR:
            raise TypeError(
                f"This node is a {self.role} node and cannot run produce_changes_summary()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_output_xml_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()

        print("Converting to XML format...")
        response = chain.invoke({"Optimised": optimised_content})
        print("Output is now in XML format")

        return response

    def produce_changes_summary(self, original_content, optimised_content):
        """
        Produces a summary of the changes that happened when rewriting original article to optimized article.

        Args:
            original_content (str): the original article content
            optimised_content (str): the optimised article content

        Returns:
              str: A response string containing the summary of the changes

        Raises:
            TypeError: a TypeError is raised if the node role does not support the function
        """

        # Raises an error if the role is not "Writing postprocessor"
        if self.role != ROLES.WRITING_POSTPROCESSOR:
            raise TypeError(
                f"This node is a {self.role} node and cannot run produce_changes_summary()"
            )

        prompt_t = ChatPromptTemplate.from_messages(
            self.prompt_template.return_changes_summariser_prompt()
        )

        chain = prompt_t | self.model | StrOutputParser()

        print("Producing summary of the changes...")
        response = chain.invoke(
            {"Original": original_content, "Optimised": optimised_content}
        )
        print("Summary of changes completed")

        return response

    def optimise_title(self, content, feedback):
        """
        The article title is generated based on the optimised article content

        Args:
            content (str): the optimised article content
            feedback (str): A string containing the feedback for optimising the article title from previous evaluation steps

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

        # Defining the optimise title prompt
        optimise_title_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_prompt("optimise title")
        )

        # Defining the shorten title prompt
        shorten_title_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_title_prompt("shorten title")
        )

        # Defining the optimise title chain
        optimise_title_chain = (
            optimise_title_prompt
            | self.model
            | StrOutputParser()
            | {"title": RunnablePassthrough()}
        )

        # Defining the shorten title chain
        shorten_title_chain = shorten_title_prompt | self.model | StrOutputParser()

        # Combining the final chain with the optimise title and shorten title chain
        chain = (
            optimise_title_chain
            | {"content": itemgetter("title")}
            | RunnableParallel(title=shorten_title_chain)
        )

        print("Optimising article title...")
        # Invoking the final optimise title chain
        response = chain.invoke({"content": content, "feedback": feedback})
        print("Article title optimised")

        # Extracting the final optimised titles from the dictionary returned by the final optimise title chain
        response = response["title"]

        return response

    def optimise_meta_desc(self, content, feedback):
        """
        The article meta description is generated based on the optimised article content

        Args:
            content (str): the optimised article content
            feedback (str): A string containing the feedback for optimising the article meta description from previous evaluation steps

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

        # Defining the optimise meta description prompt
        optimise_meta_desc_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_prompt("optimise meta desc")
        )

        # Defining the shorten meta description prompt
        shorten_meta_desc_prompt = ChatPromptTemplate.from_messages(
            self.prompt_template.return_meta_desc_prompt("shorten meta desc")
        )

        # Defining the optimise meta description chain
        optimise_meta_desc_chain = (
            optimise_meta_desc_prompt
            | self.model
            | StrOutputParser()
            | {"meta_desc": RunnablePassthrough()}
        )

        # Defining the shorten meta description chain
        shorten_meta_desc_chain = (
            shorten_meta_desc_prompt | self.model | StrOutputParser()
        )

        # Combining the optimise meta description chain with the shorten meta description chain to form the final chain
        chain = (
            optimise_meta_desc_chain
            | {"content": itemgetter("meta_desc")}
            | RunnableParallel(meta_desc=shorten_meta_desc_chain)
        )

        print("Optimising article meta description...")
        # Invoking the final optimise meta description chain
        response = chain.invoke({"content": content, "feedback": feedback})
        print("Article meta description optimised")

        # Extracting the final optimised meta description from the dictionary returned by the final optimise meta description chain
        response = response["meta_desc"]
        return response
