import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from models import start_llm

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

"""
Declaring constants
"""
# Available models
MODELS = ["Mistral", "Llama3"]

# Declaring model to use
MODEL = MODELS[0]

# Declaring node roles
NODE_ROLES = [
    "Researcher",
    "Comparer",
    "Meta description",
    "Title",
    "Content guidelines",
    "Writing guidelines",
]
RESEARCHER = NODE_ROLES[0]
COMPARER = NODE_ROLES[1]
META_DESC = NODE_ROLES[2]
TITLE = NODE_ROLES[3]
CONTENT_GUIDELINES = NODE_ROLES[4]
WRITING_GUIDELINES = NODE_ROLES[5]

# Declaring maximum new tokens
MAX_NEW_TOKENS = 3000

ROOT = os.getcwd()
EXTRACTED_TEXT_DIRECTORY = (
    f"{ROOT}/content-optimization/data/02_intermediate/all_extracted_text/"
)
ARTICLE_CATEGORY = "diseases-and-conditions/"
# Key in the title of the articles here
ARTICLE1_TITLE = "Diabetic Foot Ulcer_ Symp_1437648.txt"
ARTICLE2_TITLE = "Diabetic Foot Care_1437355.txt"


class GraphState(TypedDict):
    articles: Optional[
        list
    ]  # A list where each element is a String with the article content
    keypoints: Optional[
        list
    ]  # A list where each element is a String with the article keypoints
    response: Optional[str]
    counter: Optional[int]
    previous_node: Optional[str]
    writing_guidelines: Optional[bool]
    content_guidelines_optimisation: Optional[bool]
    title_optimisation: Optional[bool]
    meta_desc_optimisation: Optional[bool]
    prev_node: Optional[str]


workflow = StateGraph(GraphState)


def researcher_node(state):
    """Creates a researcher node
    Args:
        state: this is a GraphState object

    Returns:
        a dictionary with updated "keypoints" and "counter", which will be reflected in the GraphState object
    """
    article_list = state.get("articles", "")
    counter = state.get("counter", 0)
    print("This is article ", counter + 1)
    keypoints = state.get("keypoints", [])
    article = article_list[counter].strip()
    article_keypoints = researcher_agent.generate_text(article)
    new_article_keypoints = article_keypoints
    keypoints.append(new_article_keypoints)
    return {"keypoints": keypoints, "counter": counter + 1}


def compiler_node(state):
    keypoints = state.get("keypoints")
    print("this is keypoints", len(keypoints))
    compiled_keypoints = comparer_agent.compile_points(keypoints)
    return {"response": compiled_keypoints}


def meta_description_node(state):

    return {}


def title_optimisation_node(state):
    return {}


def content_guidelines_node(state):
    pass


def writing_guidelines_node(state):
    pass


# Adding the nodes to the workflow
workflow.add_node("researcher_node", researcher_node)
workflow.add_node("compiler_node", compiler_node)
workflow.add_node("meta_description_node", meta_description_node)
workflow.add_node("title_optimisation_node", title_optimisation_node)
workflow.add_node("content_guidelines_node", content_guidelines_node)
workflow.add_node("writing_guidelines_node", writing_guidelines_node)


def decide_next_node(state):
    return (
        "researcher_node"
        if state.get("counter") < article_list_length
        else "compiler_node"
    )


def decide_next_optimisation_node(state):
    if state.get("content_guidelines_optimisation"):
        return "content_guidelines_node"
    elif state.get("title_optimisation"):
        return "title_optimisation_node"
    elif state.get("meta_desc_optimisation"):
        return "meta_description_node"
    else:
        return "END"


workflow.add_conditional_edges(
    "researcher_node",
    decide_next_node,
    {"researcher_node": "researcher_node", "compiler_node": "compiler_node"},
)

workflow.add_conditional_edges(
    "compiler_node",
    decide_next_optimisation_node,
    {
        "content_guidelines_node": "content_guidelines_node",
        "title_optimisation_node": "title_optimisation_node",
        "meta_description_node": "meta_description_node",
        "END": END,
    },
)

workflow.add_conditional_edges(
    "writing_guidelines_node",
    decide_next_optimisation_node,
    {
        "title_optimisation_node": "title_optimisation_node",
        "meta_description_node": "meta_description_node",
        "END": END,
    },
)

workflow.add_conditional_edges(
    "title_optimisation_node",
    decide_next_optimisation_node,
    {"meta_description_node": "meta_description_node", "END": END},
)

# Setting entry point node
workflow.set_entry_point("researcher_node")
# workflow.add_edge('compiler_node', END)

# Edges connecting compiler_node to other nodes
# workflow.add_edge('compiler_node', "meta_description_node")
# workflow.add_edge('compiler_node', "title_optimisation_node")
# workflow.add_edge('compiler_node', "content_guidelines_node")

# Edge connecting content_guidelines_node to writing_guidelines_node
workflow.add_edge("content_guidelines_node", "writing_guidelines_node")

# All edges connecting to END
workflow.add_edge("meta_description_node", END)
workflow.add_edge("title_optimisation_node", END)
workflow.add_edge("writing_guidelines_node", END)

app = workflow.compile()

# starting up respective llm agents
researcher_agent = start_llm(MODEL, RESEARCHER)
comparer_agent = start_llm(MODEL, COMPARER)
meta_desc_agent = start_llm(MODEL, META_DESC)
title_agent = start_llm(MODEL, TITLE)
content_guidelines_agent = start_llm(MODEL, CONTENT_GUIDELINES)
writing_guidelines_agent = start_llm(MODEL, WRITING_GUIDELINES)

# load the articles
with open(f"{EXTRACTED_TEXT_DIRECTORY}{ARTICLE_CATEGORY}{ARTICLE1_TITLE}", "r") as file:
    article_1 = file.read()
with open(f"{EXTRACTED_TEXT_DIRECTORY}{ARTICLE_CATEGORY}{ARTICLE2_TITLE}", "r") as file:
    article_2 = file.read()

article_list = [article_1, article_2]
article_list_length = len(article_list)

inputs = {"articles": article_list, "keypoints": [], "counter": 0}

result = app.invoke(inputs)
for i in range(0, 2):
    print("THIS IS KEYPOINTS")
    print(str(result["keypoints"][i]))
    print("-----------------")
print("THIS IS THE RESPONSE")
print(str(result["response"]))
