import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import MessagesState
from utils.evaluations import calculate_readability

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
    flag_for_content_judge: dict[str, bool]
    flag_for_title_judge: dict[str, bool]
    flag_for_meta_desc_judge: dict[str, bool]
    content_judge: Optional[str]
    title_judge: Optional[str]
    meta_desc_judge: Optional[str]

    # Nodes
    def content_evaluation_node(state: MessagesState) -> str:
        article_content = state.get("article_content", "")
        content_flags = state.get("content_flags", {})

        # Check readability -
        # Hemmingway Metric
        metric = calculate_readability(article_content, "hemmingway")
        score = metric.get("score", -1)

        if score <= 0:
            raise ValueError("The readability score must be greater than 0.")
        elif score >= 10:
            content_flags.update({"is_unreadable": True})
        else:
            content_flags.update({"is_unreadable": False})

        # Check for insufficient content -
        # Less than 300 - 400 words is considered too brief
        # to adequately cover a topic unless it's a very specific and narrow subject
        # TODO: Plot the word count distribution of articles across each content category
        word_count = len(article_content.split())
        if word_count < 300:
            content_flags.update({"low_word_count": True})
        else:
            content_flags.update({"low_word_count": False})

        return {"flags_for_content_judge": content_flags}

    def content_explanation_node(state: MessagesState) -> str:
        # Check poor content structure -
        # No clear sections
        # No introduction or conclusion
        # Absence of headings or subheadings

        # Check whether the writing guideline is followed given the tagged topic
        # Refer to Content Playbook - https://drive.google.com/file/d/1I6k4FDiX8zsARs4DAPnkhbtUl71K-bhv/view
        pass

    def title_evaluation_node(state: MessagesState) -> str:
        article_title = state.get("article_title", "")
        title_flags = state.get("flag_for_title_judge", {})

        # Not Within Page Title Char Count - Up to 70 Characters
        # TODO: Check whether an error is raised for all articles - Stress test
        char_count = len(article_title)
        if char_count <= 0:
            raise ValueError("The title character count must be greater than 0.")
        elif char_count > 70:
            title_flags.update({"long_title": True})
        else:
            title_flags.update({"long_title": False})

        return {"flags_for_title_judge": title_flags}

    def title_explanation_node(state: MessagesState) -> str:
        # Irrelevant Page Title
        
        pass

    def meta_desc_evaluation_node(state: MessagesState) -> str:
        meta_desc = state.get("meta_desc", "")
        meta_flags = state.get("flag_for_meta_desc_judge", {})

        # Not Within Meta Description Char Count - Between 70 and 160 characters
        char_count = len(meta_desc)
        if char_count <= 0:
            raise ValueError("The meta description character count must be greater than 0.")
        elif 70 <= char_count <= 160:
            meta_flags.update({"poor_meta_desc": False})
        else:
            meta_flags.update({"poor_meta_desc": True})

        return {"flags_for_meta_desc_judge": meta_flags}

    def meta_desc_explanation_node(state: MessagesState) -> str:
        # Irrelevant Meta Description

        pass
