import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import MessagesState

# Setting the environment for HuggingFaceHub
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
os.environ["PHOENIX_PROJECT_NAME"] = os.getenv("PHOENIX_PROJECT_NAME", "")

# Available models configured to the project
MODELS = ["mistral", "llama3"]

# Declaring model to use
MODEL = MODELS[1]

# Declaring node roles
RESEARCHER = "Researcher"
COMPILER = "Compiler"
META_DESC = "Meta description"
TITLE = "Title"
CONTENT_GUIDELINES = "Content guidelines"
WRITING_GUIDELINES = "Writing guidelines"

# Declaring maximum new tokens
MAX_NEW_TOKENS = 3000


class GraphState(TypedDict):
    """This class contains the different keys relevant to the project. It inherits from the TypedDict class.

    Attributes:
        article_content: A required String where each element is a String containing the article content.
        article_title: A required String which will contain the article title.
        meta_desc: A required String that will contain article's meta description.
        content_judge: A
    """

    # Attributes / Input parameters
    article_content: str
    article_title: str
    meta_desc: str
    flag_for_content_judge: bool
    flag_for_title_judge: bool
    flag_for_meta_desc_judge: bool
    content_judge: Optional[str]
    title_judge: Optional[str]
    meta_desc_judge: Optional[str]

    # Nodes
    def content_evaluation_node(state: MessagesState) -> str:
        # Check readability

        # Check poor content structure

        # Check for insufficient content

        # Check whether the writing guideline is followed given the tagged topic
        pass

    def content_explanation_node(state: MessagesState) -> str:
        pass

    def title_evaluation_node(state: MessagesState) -> str:
        pass

    def title_explanation_node(state: MessagesState) -> str:
        pass

    def meta_desc_evaluation_node(state: MessagesState) -> str:
        pass

    def meta_desc_explanation_node(state: MessagesState) -> str:
        pass
