from enum import Enum

from config import settings


class MODELS(Enum):
    """Enumeration of supported AI models.

    This enum represents the various AI models available for use in the application.
    It includes models from different providers such as Meta, Microsoft, and Mistral.

    Attributes:
        LLAMA3: Meta's Llama 3 model (from HuggingFace).
        PHI3: Microsoft's Phi-3 model (from HuggingFace).
        MISTRAL: Mistral AI's Instruct model (from HuggingFace).
        AZURE: Azure deployment model (name fetched from settings).
    """

    LLAMA3 = "meta-llama/Meta-Llama-3-8B-Instruct"
    PHI3 = "microsoft/Phi-3-mini-128k-instruct"
    MISTRAL = "mistralai/Mistral-7B-Instruct-v0.3"
    AZURE = settings.AZURE_DEPLOYMENT_NAME

    @classmethod
    def _missing_(cls, name: str):
        name = name.lower()
        for member in cls:
            if member.name.lower() == name:
                return member
        return None


class ROLES(Enum):
    """Enumeration of AI Agentic Roles.

    This enum represents the various AI agents used in the article evaluation and rewriting workflow.

    Attributes:
          EVALUATOR: Evaluator LLM to evaluate (i.e. decide and summarise evaluations) in Optimisation Checks Graph
          EXPLAINER: Explainer LLM to explain rule-based approaches (e.g. poor readability) used to evaluate articles
          RESEARCHER: Researcher LLM to extract keypoints from the article content and determine sentences to omit
          COMPILER: Compiler LLM to compile keypoints across multiple article contents
          META_DESC: Meta Description LLM to generate the article meta description based on the optimised article content
          TITLE: Meta Description LLM to generate the article title based on the optimised article content
          CONTENT_OPTIMISATION: Content Optimisation LLM to enhance the article content and structure based on the keypoints
          WRITING_OPTIMISATION: Writing Optimisation LLM to optimise the article content based on the provided writing style
          READABILITY_EVALUATION: Readability Evaluation LLM to evaluate the readability of the generated article content
          READABILITY_OPTIMISATION: Readability Evaluation LLM to optimise the readability of the generated article content
          PERSONALITY_EVALUATION: Personality Evaluation LLM to evaluate the writing style of the generated article content
          WRITING_POSTPROCESSOR: Writing postprocessor LLM to summarise the changes between the original article and the optimized article and output the latter in XML format
    """

    # Declaring node roles
    EVALUATOR = "Evaluator"
    EXPLAINER = "Explainer"
    RESEARCHER = "Researcher"
    COMPILER = "Compiler"
    META_DESC = "Meta description optimisation"
    TITLE = "Title optimisation"
    CONTENT_OPTIMISATION = "Content optimisation"
    WRITING_OPTIMISATION = "Writing optimisation"
    READABILITY_EVALUATION = "Readability evaluation"
    READABILITY_OPTIMISATION = "Readability optimisation"
    PERSONALITY_EVALUATION = "Personality evaluation"
    WRITING_POSTPROCESSOR = "Writing postprocessor"
