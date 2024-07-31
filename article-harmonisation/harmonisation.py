from typing import Optional, TypedDict

from agents.enums import MODELS, ROLES
from agents.models import LLMInterface, start_llm
from config import settings
from langgraph.graph import END, START
from utils.formatters import concat_headers_to_content, print_checks
from utils.graphs import create_graph, draw_graph, execute_graph
from utils.paths import get_root_dir

# Declaring maximum new tokens
MAX_NEW_TOKENS = settings.MAX_NEW_TOKENS

# Declaring model to use
MODEL = MODELS("llama3").name


class OriginalArticle(TypedDict):
    article_content: list
    article_title: Optional[str]
    meta_desc: Optional[str]


class OptimisedArticle(TypedDict):
    researcher_keypoints: Optional[list]
    article_researcher_counter: Optional[int]
    compiled_keypoints: Optional[str]
    optimised_content: Optional[str]
    optimised_writing: Optional[str]
    optimised_article_title: Optional[str]
    optimised_meta_desc: Optional[str]


class OptimisationFlags(TypedDict):
    flag_for_content_optimisation: bool
    flag_for_title_optimisation: bool
    flag_for_meta_desc_optimisation: bool


class LLMAgents(TypedDict):
    researcher_agent: LLMInterface
    compiler_agent: LLMInterface
    content_optimisation_agent: LLMInterface
    writing_optimisation_agent: LLMInterface
    title_optimisation_agent: LLMInterface
    meta_desc_optimisation_agent: LLMInterface


class RewritingState(TypedDict):
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

    original_article_content: OriginalArticle
    optimised_article_output: OptimisedArticle
    user_flags: OptimisationFlags
    llm_agents: LLMAgents


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
    article_list = state.get("original_article_content")["article_content"]
    counter = state.get("optimised_article_output")["article_researcher_counter"]
    article = article_list[counter]
    keypoints = state.get("optimised_article_output")["researcher_keypoints"]
    researcher_agent = state.get("llm_agents")["researcher_agent"]

    print("Processing keypoints for article", counter + 1)
    processed_keypoints = ""
    print(f"Number of keypoints in article {counter + 1}: ", len(article))

    # Stores the number of keypoints processed in the current article
    kp_counter = 0

    # For loop iterating through each keypoint in each article
    for kp in article:
        kp_counter += 1
        article_keypoints = researcher_agent.generate_keypoints(kp, kp_counter)
        processed_keypoints += f"{article_keypoints} \n"
    keypoints.append(processed_keypoints)

    return {
        "optimised_article_output": {
            "researcher_keypoints": keypoints,
            "article_researcher_counter": counter + 1,
        }
    }


def compiler_node(state):
    """Creates a compiler node, which will compile the keypoints from a list of keypoints

    Args:
        state:  a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "compiled_keypoints"
            - compiled_keypoints: a String containing the compiled keypoints from the compiler LLM
    """
    optimised_article_output = state.get("optimised_article_output")
    keypoints = optimised_article_output["researcher_keypoints"]

    # Runs the compiler LLM to compile the keypoints
    compiler_agent = state.get("llm_agents")["compiler_agent"]

    compiled_keypoints = compiler_agent.compile_points(keypoints)
    optimised_article_output["compiled_keypoints"] = compiled_keypoints

    return {"optimised_article_output": optimised_article_output}


def meta_description_optimisation_node(state):
    """Creates a meta description optimisation node, which will optimise the meta description of the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "meta_desc",  "flag_for_meta_desc_optimisation"
            - meta_desc: a String containing the optimised meta description from the meta description optimisation LLM
            - flag_for_meta_desc_optimisation: a False boolean value to indicate that the meta description optimisation step has been completed
    """
    optimised_article_output = state.get("optimised_article_output")

    content = optimised_article_output["researcher_keypoints"]
    if "optimised_writing" in optimised_article_output.keys():
        content = optimised_article_output["optimised_writing"]

    meta_desc_optimisation_agent = state.get("llm_agents")[
        "meta_desc_optimisation_agent"
    ]
    optimised_meta_desc = meta_desc_optimisation_agent.optimise_meta_desc(content)

    optimised_article_output["optimised_meta_desc"] = optimised_meta_desc

    user_flags = state.get("user_flags")
    user_flags["flag_for_meta_desc_optimisation"] = False

    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
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
    optimised_article_output = state.get("optimised_article_output")

    content = optimised_article_output["researcher_keypoints"]
    if "optimised_writing" in optimised_article_output.keys():
        content = optimised_article_output["optimised_writing"]

    title_optimisation_agent = state.get("llm_agents")["title_optimisation_agent"]
    optimised_article_title = title_optimisation_agent.optimise_title(content)

    optimised_article_output["optimised_article_title"] = optimised_article_title

    user_flags = state.get("user_flags")
    user_flags["flag_for_title_optimisation"] = False

    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
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
    optimised_article_output = state.get("optimised_article_output")

    keypoints = optimised_article_output["researcher_keypoints"]
    if "compiled_keypoints" in optimised_article_output.keys():
        keypoints = optimised_article_output["compiled_keypoints"]

    # Runs the compiler LLM to compile the keypoints
    content_optimisation_agent = state.get("llm_agents")["content_optimisation_agent"]

    optimised_content = content_optimisation_agent.optimise_content(keypoints)

    optimised_article_output["optimised_content"] = optimised_content

    return {"optimised_article_output": optimised_article_output}


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
    optimised_article_output = state.get("optimised_article_output")

    optimised_content = optimised_article_output["optimised_content"]
    writing_optimisation_agent = state.get("llm_agents")["writing_optimisation_agent"]
    optimised_writing = writing_optimisation_agent.optimise_writing(optimised_content)

    user_flags = state.get("user_flags")
    user_flags["flag_for_content_optimisation"] = False

    optimised_article_output["optimised_writing"] = optimised_writing

    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
    }


# functions to determine next node
def check_all_articles(state):
    """Checks if all articles have gone through the researcher LLM and determines if the state should return to the researcher node or move on to the compiler node. This node also determines if this is a harmonisation or optimisation process.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "researcher_node": returned if counter < number of articles to be harmonised
        "compiler_node": returned if counter >= number of articles to be harmonised
    """
    researcher_counter = state.get("optimised_article_output")[
        "article_researcher_counter"
    ]
    article_content = state.get("original_article_content")["article_content"]
    content_optimisation_flags = state.get("user_flags")[
        "flag_for_content_optimisation"
    ]
    if researcher_counter < len(article_content):
        return "researcher_node"
    elif (len(article_content) < 2) and content_optimisation_flags:
        return "content_guidelines_optimisation_node"
    else:
        return "compiler_node"


def decide_next_optimisation_node(state):
    """Checks user flags for content optimisation, title optimisation and meta description in state, and returning the appropriate node depending on the stored boolean values of each flag.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "content_guidelines_node": returned if flag_for_content_optimisation is True
        "title_optimisation_node": returned if previous flag is False and flag_for_title_optimisation is True
        "meta_description_node": returned if previous flags are False and flag_for_meta_desc_optimisation is True
        END: returned if all flags are False, as no further optimisation is required for the article
    """
    content_optimisation_flags = state.get("user_flags")[
        "flag_for_content_optimisation"
    ]
    title_optimisation_flags = state.get("user_flags")["flag_for_title_optimisation"]
    meta_desc_optimisation_flags = state.get("user_flags")[
        "flag_for_meta_desc_optimisation"
    ]

    if content_optimisation_flags:
        return "content_guidelines_optimisation_node"
    elif title_optimisation_flags:
        return "title_optimisation_node"
    elif meta_desc_optimisation_flags:
        return "meta_description_optimisation_node"
    else:
        return "__end__"


# Adds a conditional edge to the workflow from researcher node to compiler node
workflow.add_conditional_edges(
    "researcher_node",
    check_all_articles,
    {
        "researcher_node": "researcher_node",
        "compiler_node": "compiler_node",
        "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
    },
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


def draw_graph(graph, filepath: str):
    img = graph.get_graph(xray=True).draw_mermaid_png()
    with open(filepath, "wb") as f:
        f.write(img)


def execute_graph(workflow: StateGraph, input: dict[str, Any]) -> dict[str, Any]:
    # Set up LLM tracing session
    px.launch_app()
    LangChainInstrumentor().instrument()

    # Run LangGraph Application
    app = workflow.compile()
    result = app.invoke(input=input)
    draw_graph(
        app,
        "/Users/jin/Documents/GitHub/healthhub-content-optimization/article-harmonisation/docs/images/graph.png",
    )

    # Prints the various checks
    print_checks(result, MODEL)

    # trace_df = px.Client().get_spans_dataframe()
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # trace_df.to_parquet(f"traces-{timestr}.parquet", index=False)

    px.close_app()

    return result


if __name__ == "__main__":
    # starting up the respective llm agents
    researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
    compiler_agent = start_llm(MODEL, ROLES.COMPILER)
    meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC)
    title_optimisation_agent = start_llm(MODEL, ROLES.TITLE)
    content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
    writing_optimisation_agent = start_llm(MODEL, ROLES.WRITING_OPTIMISATION)

    # List with the articles to harmonise
    article_list = ["Rubella", "How Dangerous Is Rubella?"]

    processed_input_articles = concat_headers_to_content(article_list)

    # Dictionary with the variouse input keys and items
    inputs = {
        "original_article_content": {"article_content": processed_input_articles},
        "optimised_article_output": {
            "researcher_keypoints": [],
            "article_researcher_counter": 0,
        },
        "user_flags": {
            "flag_for_content_optimisation": True,
            "flag_for_title_optimisation": True,
            "flag_for_meta_desc_optimisation": True,
        },
        "llm_agents": {
            "researcher_agent": researcher_agent,
            "compiler_agent": compiler_agent,
            "content_optimisation_agent": content_optimisation_agent,
            "writing_optimisation_agent": writing_optimisation_agent,
            "title_optimisation_agent": title_optimisation_agent,
            "meta_desc_optimisation_agent": meta_desc_optimisation_agent,
        },
    }

    result = execute_graph(app, inputs)

    # Prints the various checks
    print_checks(result, MODEL)

    print(result)
