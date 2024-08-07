from enum import Enum


class MODELS(Enum):
    """
    # Meta Llama
    # "meta-llama/Meta-Llama-3-8B-Instruct",
    # "meta-llama/Meta-Llama-3.1-8B-Instruct",
    # Phi 3
    # "microsoft/Phi-3-mini-128k-instruct",
    # Mistral
    # "mistralai/Mistral-7B-Instruct-v0.3",
    # "NousResearch/Hermes-2-Pro-Mistral-7B",
    """

    llama3 = "meta-llama/Meta-Llama-3-8B-Instruct"
    phi3 = "microsoft/Phi-3-mini-128k-instruct"
    mistral = "mistralai/Mistral-7B-Instruct-v0.3"
    azure = "gpt-35-turbo-0125"

    @classmethod
    def _missing_(cls, name: str):
        name = name.lower()
        for member in cls:
            if member.name.lower() == name:
                return member
        return None


class ROLES(Enum):
    # Declaring node roles
    EVALUATOR = "Evaluator"
    EXPLAINER = "Explainer"
    RESEARCHER = "Researcher"
    COMPILER = "Compiler"
    META_DESC = "Meta description optimisation"
    TITLE = "Title optimisation"
    CONTENT_OPTIMISATION = "Content optimisation"
    WRITING_OPTIMISATION = "Writing optimisation"
    WRITING_EVALUATION = "Writing evaluation"
    READABILITY_OPTIMISATION = "Readability optimisation"
    PERSONALITY_EVALUATION = "Personality evaluation"
