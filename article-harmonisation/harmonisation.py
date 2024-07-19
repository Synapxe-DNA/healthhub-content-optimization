import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from models import start_llm

# Setting the environment for HuggingFaceHub
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

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

# Declaring directorys
ROOT = os.getcwd()
EXTRACTED_TEXT_DIRECTORY = (
    f"{ROOT}/content-optimization/data/02_intermediate/all_extracted_text/"
)
ARTICLE_CATEGORY = "diseases-and-conditions/"

# Declaring title of the articles here. Currently only 2 articles are used and this section is declared at the start, which is bound to change with further developments.
ARTICLE1_TITLE = "Diabetic Foot Ulcer_ Symp_1437648.txt"
ARTICLE2_TITLE = "Diabetic Foot Care_1437355.txt"


def print_checks(result):
    """Prints out the various key outputs in graph. Namely, it will help you check for
        1. Researcher LLM outputs -> keypoints: prints out the sentences in their respective categories, including sentences omitted by the llm
        2. Compiler LLM outputs -> compiled_keypoints: prints out the compiled key points
        3. Content optimisation LLM outputs -> optimised_content: prints out the optimised article content after optimisation by content and writing guideline LLM
        4. Title optimisation LLM outputs -> article_title: prints out the optimised title
        5. Meta description optimisation LLM outputs -> meta_desc: prints out the optimised meta description

    Args:
        result: a AddableValuesDict object containing the final outputs from the graph
    """

    # determines the number of articles undergoing the harmonisation process
    num_of_articles = len(result["article_content"])
    

    f = open(f"article-harmonisation/docs/txt_outputs/{MODEL}_compiled_keypoints_check.txt", "w")
    f.write("This is article 1 \n")
    f.write(article_1 + "\n")
    f.write("This is article 2 \n")
    f.write(article_2 + "\n")


    # printing each keypoint produced by researcher LLM
    print("\n RESEARCHER LLM CHECKS \n\n ----------------- \n", file=f)
    for i in range(0, num_of_articles):
        print(f"These are the keypoints for article {i+1}".upper(), file = f)
        print(str(result["keypoints"][i]), file = f)
        print(" \n ----------------- \n", file = f)

    # printing compiled keypoints produced by compiler LLM
    
    print("COMPILER LLM CHECKS \n\n ----------------- \n", file = f)
    print(str(result["compiled_keypoints"]), file=f)
    print(" \n ----------------- \n", file = f)

    # checking for optimised content produced by content optimisation flow
    flags = {"optimised_content", "article_title", "meta_desc"}
    keys = result.keys()
    print("CONTENT OPTIMISATION CHECKS \n\n ----------------- \n", file = f)
    for flag in flags:
        if flag in keys:
            print(f"These are the optimised {flag.upper()}", file=f)
            print(result[flag], file=f)
            print(" \n ----------------- \n",file=f)
        else:
            print(f"{flag.upper()} has not been flagged for optimisation.",file=f)
            print(" \n ----------------- \n",file=f)
    f.close()

class GraphState(TypedDict):
    """This class contains the different keys relevant to the project. It inherits from the TypedDict class.

    Attributes:
        article_content: A required list where each element is a String containing the article content.
        article_title: An optional String which will contain the article title.
        meta_desc: An optional String that will contain article's meta description.
        keypoints: An optional list where each element is a String with the article keypoints.
        compiled_keypoints: An optional String containing keypoints compiled from the attribute keypoints.
        optimised_content: An optional String containing the final optimised content.
        article_researcher_counter: An optional integer serving as a counter for number of articles processed by the researcher node.
        previous_node: An optional String that will store the name of the most recently visited node by the StateGraph. 
        flag_for_content_optimisation: A required boolean value, determining if the user has flagged the article for content optimisation.
        flag_for_title_optimisation: A required boolean value, determining if the user has flagged the article for title optimisation.
        flag_for_meta_desc_optimisation: A required boolean value, determining if the user has flagged the article for meta description optimisation.

    """

    article_content: list
    article_title: Optional[str]
    meta_desc: Optional[str]
    keypoints: Optional[list]
    compiled_keypoints: Optional[str]
    optimised_content: Optional[str]
    article_researcher_counter: Optional[int]
    # previous_node: Optional[str]
    flag_for_content_optimisation: bool
    flag_for_title_optimisation: bool
    flag_for_meta_desc_optimisation: bool


# Functions defining the functionality of different nodes
def researcher_node(state):
    """Creates a researcher node, which will categorise the sentences in the article into keypoints.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "keypoints", "article_researcher_counter"
            - keypoints: an updated list storing keypoints from all articles output from the researcher node
            - article_researcher_counter: an integer serving as a counter for number of articles processed by the researcher node
    """
    article_list = state.get("article_content", "")
    counter = state.get("article_researcher_counter", 0)
    print("This is article ", counter + 1)
    keypoints = state.get("keypoints", [])
    article = article_list[counter].strip()

    # Runs the researcher LLM agent
    article_keypoints = researcher_agent.generate_keypoints(article)
    keypoints.append(article_keypoints)
    return {"keypoints": keypoints, "article_researcher_counter": counter + 1}


def compiler_node(state):
    """Creates a compiler node, which will compile the keypoints from a list of keypoints

    Args:
        state:  a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "compiled_keypoints"
            - compiled_keypoints: a String containing the compiled keypoints from the compiler LLM
    """
    keypoints = state.get("keypoints")
    print("this is keypoints", len(keypoints))

    # Runs the compiler LLM to compile the keypoints
    compiled_keypoints = compiler_agent.compile_points(keypoints)
    return {"compiled_keypoints": compiled_keypoints}


def meta_description_optimisation_node(state):
    """Creates a meta description optimisation node, which will optimise the meta description of the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "meta_desc",  "flag_for_meta_desc_optimisation"
            - meta_desc: a String containing the optimised meta description from the meta description optimisation LLM
            - flag_for_meta_desc_optimisation: a False boolean value to indicate that the meta description optimisation step has been completed
    """

    return {
        "meta_desc": "This is the meta desc",
        "flag_for_meta_desc_optimisation": False,
    }


def title_optimisation_node(state):
    """Creates a title optimisation node, which will optimise the title of the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "article_title",  "flag_for_title_optimisation"
            - article_title: a String containing the optimised title from the title optimisation LLM
            - flag_for_title_optimisation: a False boolean value to indicate that the title optimisation step has been completed
    """
    return {
        "article_title": "This is new article title",
        "flag_for_title_optimisation": False,
    }


def content_guidelines_optimisation_node(state):
    """Creates a content guidelines node, which will rewrite missing content of the article based on the article topic's requirements state in the content playbook.

        Requirements for each topic can be found in the content playbook under:
            1. Chapter 3, Step 1, (iii) writing guide
    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "optimised_content"
            - optimised_content: a String containing the rewritten article from the content guidelines LLM
    """
    return {"optimised_content": "This is content"}


def writing_guidelines_optimisation_node(state):
    """Creates a writing optimisation node, which will optimise the article content based on the writing guidelines from the content playbook

        Content covered from the playbook include:
            1. Chapter 1, Section A, Guidelines + Examples

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "optimised_content",  "flag_for_content_optimisation"
            - optimised_content: a String containing the optimised content from the writing optimisation LLM
            - flag_for_content_optimisation: a False boolean value to indicate that the writing optimisation step has been completed
    """
    optimised_content = state.get("optimised_content")
    optimised_content += " And this is writing guidelines"
    return {
        "optimised_content": optimised_content,
        "flag_for_content_optimisation": False,
    }

# creating a StateGraph object with GraphState as input.
workflow = StateGraph(GraphState)
# Adding the nodes to the workflow
workflow.add_node("researcher_node", researcher_node)
workflow.add_node("compiler_node", compiler_node)
workflow.add_node(
    "meta_description_optimisation_node", meta_description_optimisation_node
)
workflow.add_node("title_optimisation_node", title_optimisation_node)
workflow.add_node(
    "content_guidelines_optimisation_node", content_guidelines_optimisation_node
)
workflow.add_node(
    "writing_guidelines_optimisation_node", writing_guidelines_optimisation_node
)


# functions to determine next node
def check_all_articles(state):
    """Checks if all articles have gone through the researcher LLM and determines if the state should return to the researcher node or move on to the compiler node

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "researcher_node": returned if counter < number of articles to be harmonised
        "compiler_node": returned if counter >= number of articles to be harmonised
    """

    return (
        "researcher_node"
        if state.get("article_researcher_counter") < article_list_length
        else "compiler_node"
    )


def decide_next_optimisation_node(state):
    """Checks user flags for content optimisation, title optimisation and meta description in state, and returning the appropriate node depending on the stored boolean values of each flag.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "content_guidelines_node": returned if flag_for_content_optimisation is True
        "title_optimisation_node": returned if previous flag is False and flag_for_title_optimisation is True
        "meta_description_node": returned if previous flags are False and flag_for_meta_desc_optimisation is True
        "__end__": returned if all flags are False, as no further optimisation is required for the article
    """
    if state.get("flag_for_content_optimisation"):
        return "content_guidelines_optimisation_node"
    elif state.get("flag_for_title_optimisation"):
        return "title_optimisation_node"
    elif state.get("flag_for_meta_desc_optimisation"):
        return "meta_description_optimisation_node"
    else:
        return "__end__"


# Adds a conditional edge to the workflow from researcher node to compiler node
workflow.add_conditional_edges(
    "researcher_node",
    check_all_articles,
    {"researcher_node": "researcher_node", "compiler_node": "compiler_node"},
)

# Adds a conditional edge to the workflow from compiler node to content guidelines node, title optimmisation node, meta description optimisation node and END
workflow.add_conditional_edges(
    "compiler_node",
    decide_next_optimisation_node,
    {
        "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
        "title_optimisation_node": "title_optimisation_node",
        "meta_description_optimisation_node": "meta_description_optimisation_node",
        "__end__": END,
    },
)

# Adds a conditional edge to the workflow from compiler node to title optimmisation node, meta description optimisation node and END
workflow.add_conditional_edges(
    "writing_guidelines_optimisation_node",
    decide_next_optimisation_node,
    {
        "title_optimisation_node": "title_optimisation_node",
        "meta_description_optimisation_node": "meta_description_optimisation_node",
        "__end__": END,
    },
)

# Adds a conditional edge to the workflow from compiler node to meta description optimisation node and END
workflow.add_conditional_edges(
    "title_optimisation_node",
    decide_next_optimisation_node,
    {
        "meta_description_optimisation_node": "meta_description_optimisation_node",
        "__end__": END,
    },
)

# Setting researcher_node as the entry point for the workflow
workflow.set_entry_point("researcher_node")

# Adding an edge connecting content_guidelines_optimisation_node to writing_guidelines_optimisation_node in the workflow
workflow.add_edge(
    "content_guidelines_optimisation_node", "writing_guidelines_optimisation_node"
)

# Compiling the workflow
app = workflow.compile()

# starting up the respective llm agents
researcher_agent = start_llm(MODEL, RESEARCHER)
compiler_agent = start_llm(MODEL, COMPILER)
meta_desc_agent = start_llm(MODEL, META_DESC)
title_agent = start_llm(MODEL, TITLE)
content_guidelines_agent = start_llm(MODEL, CONTENT_GUIDELINES)
writing_guidelines_agent = start_llm(MODEL, WRITING_GUIDELINES)

# loading the articles
with open(f"{EXTRACTED_TEXT_DIRECTORY}{ARTICLE_CATEGORY}{ARTICLE1_TITLE}", "r") as file:
    article_1 = file.read()
with open(f"{EXTRACTED_TEXT_DIRECTORY}{ARTICLE_CATEGORY}{ARTICLE2_TITLE}", "r") as file:
    article_2 = file.read()

# List with the articles to harmonise
article_list = [article_1, article_2]

# Number of articles to harmonise
article_list_length = len(article_list)

# Dictionary with the variouse input keys and items
inputs = {
    "article_content": article_list,
    "keypoints": [],
    "article_researcher_counter": 0,
    "flag_for_content_optimisation": False,
    "flag_for_title_optimisation": True,
    "flag_for_meta_desc_optimisation": True,
}

result = app.invoke(inputs)

# Prints the various checks
print_checks(result)
