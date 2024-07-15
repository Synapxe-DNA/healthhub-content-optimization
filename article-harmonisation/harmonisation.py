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
MODEL = MODELS[0]
NODE_ROLES = ["Researcher", "Comparer"]
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


workflow.add_node("get_keypoints", researcher_node)
workflow.add_node("compile_keypoints", compiler_node)


def decide_next_node(state):
    return (
        "get_keypoints"
        if state.get("counter") < article_list_length
        else "compile_keypoints"
    )


workflow.add_conditional_edges(
    "get_keypoints",
    decide_next_node,
    {"get_keypoints": "get_keypoints", "compile_keypoints": "compile_keypoints"},
)

workflow.set_entry_point("get_keypoints")
workflow.add_edge("compile_keypoints", END)

app = workflow.compile()

researcher_agent = start_llm(MODEL, NODE_ROLES[0])
comparer_agent = start_llm(MODEL, NODE_ROLES[1])

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
