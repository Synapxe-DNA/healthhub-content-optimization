from typing import TypedDict
import pandas as pd

from agents.enums import ROLES
from agents.models import start_llm
from config import settings
from langgraph.graph import END, START
from states.definitions import (
    ArticleEvaluation,
    ArticleInputs,
    OptimisationAgents,
    OptimisationFlags,
    OptimisedArticle,
)
from utils.evaluations import calculate_readability
from utils.formatters import concat_headers_to_content, print_checks, split_into_list
from utils.graphs import create_graph, draw_graph, execute_graph
from utils.paths import get_root_dir
from utils.excel_extractor import return_optimisation_flags

# Declaring maximum new tokens
MAX_NEW_TOKENS = settings.MAX_NEW_TOKENS

# Declaring model to use
MODEL = settings.MODEL_NAME

# Declaring the number of retries
REWRITING_TRIES = 3

# Declaring number of optimised titles as output
NUM_OF_OPTIMISED_TITLES = 3

# Declaring number of optimised meta descriptions as output
NUM_OF_OPTIMISED_META_DESC = 3


class RewritingState(TypedDict):
    """This class contains the different keys relevant to the project. It inherits from the TypedDict class.

    Attributes:
        article_rewriting_tries: stores the number of rewriting tries 
    """

    article_rewriting_tries: int
    article_evaluation: ArticleEvaluation
    original_article_inputs: ArticleInputs
    optimised_article_output: OptimisedArticle
    user_flags: OptimisationFlags
    llm_agents: OptimisationAgents


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
    article_list = state.get("original_article_inputs")["article_content"]
    keypoints = state.get("optimised_article_output")["researcher_keypoints"]
    researcher_agent = state.get("llm_agents")["researcher_agent"]

    article_titles = state.get("original_article_inputs")["article_title"]
    # For loop iterating through each article

    for idx in range(len(article_list)):
        article_title = article_titles[idx]
        print(f"Processing keypoints for article {idx + 1} of {len(article_list)}: {article_title}")
        article = article_list[idx]
        article_keypoints = researcher_agent.generate_keypoints(article)
        keypoints.append(article_keypoints)
        print(f"Finished processing keypoints for {article_title}")

    return {
        "optimised_article_output": {
            "researcher_keypoints": keypoints,
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

    # Splitting the string of optimised article meta desc into a list where each meta desc is an individual item
    optimised_article_meta_desc = split_into_list(optimised_meta_desc, NUM_OF_OPTIMISED_META_DESC)

    optimised_article_output["optimised_meta_desc"] = optimised_article_meta_desc

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

    # Splitting the string of optimised article titles into a list where each title is an individual item
    optimised_article_titles = split_into_list(optimised_article_title, NUM_OF_OPTIMISED_TITLES)

    optimised_article_output["optimised_article_title"] = optimised_article_titles

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

    optimised_content = content_optimisation_agent.optimise_content(
        keypoints
    )

    optimised_article_output["optimised_content"] = optimised_content

    user_flags = state.get("user_flags")
    user_flags["flag_for_content_optimisation"] = False

    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
    }


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

    if (content := optimised_article_output.get("optimised_writing")) is not None:  # article optimisation/harmonisation, subsequent rewrites
        pass
    elif (content := optimised_article_output.get("optimised_content")) is not None:  # article optimisation/harmonisation, first rewriting after content optimisation
        pass
    elif (content := optimised_article_output.get("compiled_keypoints")) is not None:  # article harmonisation, first rewriting without any content optimisation
        pass
    else:
        content = optimised_article_output.get("researcher_keypoints")  # article optimisation, first rewriting without any content optimisation

    writing_optimisation_agent = state.get("llm_agents")["writing_optimisation_agent"]
    optimised_writing = writing_optimisation_agent.optimise_writing(content)

    user_flags = state.get("user_flags")
    user_flags["flag_for_writing_optimisation"] = False

    # Updating the new optimised writing in the state
    optimised_article_output["optimised_writing"] = optimised_writing

    # Calculating the new readability score
    new_readability_score = calculate_readability(optimised_writing)["score"]

    # Updating the state with the new readability score
    optimised_article_output["readability_score"] = new_readability_score


    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
    }

def readability_optimisation_node(state):
    """Creates a readability optimisation node that optimises the writing based on the feedback given."""
    # Obtaining the number of rewriting_tries
    rewriting_tries = state.get("article_rewriting_tries", 0) + 1

    if rewriting_tries > REWRITING_TRIES:
        return {"article_rewriting_tries": rewriting_tries}
    
    else:
        readability_optimisation_steps = {
            1: "cutting out redundant areas",
            2: "shortening sentences",
            3: "breaking into bullet points",
            4: "simplifying complex terms",
        }

        readability_optimisation_agent = state.get("llm_agents")[
            "readability_optimisation_agent"
        ]

        optimised_article_output = state.get("optimised_article_output")

        print("## Beginning readability optimisation process ##")
        for step_num in range(1, len(readability_optimisation_steps.keys())+1):
            # Obtaining the optimised writing
            optimised_writing = optimised_article_output.get("optimised_writing")
            step=readability_optimisation_steps[step_num]

            optimised_readability_article = readability_optimisation_agent.optimise_readability(
                content=optimised_writing, step=step
            )

            # Updating state with the newly readability optimised article
            optimised_article_output["optimised_writing"] = optimised_readability_article
        print("## Readability optimisation process completed ##")

        # Calculating the new readability score
        new_readability_score = calculate_readability(optimised_readability_article)["score"]

        # Updating the state with the new readability score
        optimised_article_output["readability_score"] = new_readability_score

        print(
            f"Rewriting Tries: {rewriting_tries}, Readability score after readability optimisation: {new_readability_score}"
        )

        return {
            "article_rewriting_tries": rewriting_tries,
            "optimised_article_output": optimised_article_output,
        }


def personality_guidelines_evaluation_node(state):
    """Creates a personality guidelines evaluation node that evaluates the given content based on the voice and personality guidelines from HH content playbook

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "article_evaluation": dictionary with updated content_flags indicating if the optimised article follows the writing personality guidelines.
    """
    # Obtaining the recently readability optimised writing
    optimised_article_output = state.get("optimised_article_output")
    optimised_writing = optimised_article_output.get("optimised_writing")

    personality_evaluation_agent = state.get("llm_agents")[
        "personality_evaluation_agent"
    ]

    personality_evaluation = personality_evaluation_agent.evaluate_personality(
        content=optimised_writing
    )

    # Obtaining article_flags dict
    article_evaluation = state.get("article_evaluation", {})

    # Updating article_evaluation with the updated personality_evaluation flags
    article_evaluation["writing_has_personality"] = personality_evaluation

    return {
        "article_evaluation": article_evaluation,
    }


# functions to determine next node
def check_for_compiler(state):
    """Determines if the state should move on to the compiler node for harmonisation or other article optimisation nodes.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "researcher_node": returned if counter < number of articles to be harmonised
        "compiler_node": returned if counter >= number of articles to be harmonised
    """

    article_content = state.get("original_article_inputs")["article_content"]
    content_optimisation_flag = state.get("user_flags")["flag_for_content_optimisation"]
    writing_optimisation_flag = state.get("user_flags")["flag_for_writing_optimisation"]
    title_optimisation_flag = state.get("user_flags")["flag_for_title_optimisation"]
    meta_desc_optimisation_flag = state.get("user_flags")[
        "flag_for_meta_desc_optimisation"
    ]

    if len(article_content) < 2:
        if content_optimisation_flag:
            return "content_guidelines_optimisation_node"
        elif writing_optimisation_flag:
            return "writing_guidelines_optimisation_node"
        elif title_optimisation_flag:
            return "title_optimisation_node"
        elif meta_desc_optimisation_flag:
            return "meta_description_optimisation_node"
        else:
            return END
    else:
        return "compiler_node"


def decide_next_optimisation_node(state):
    """Checks user flags for content optimisation, title optimisation and meta description in state, and returning the appropriate node depending on the stored boolean values of each flag.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "content_guidelines_optimisation_node": returned if flag_for_content_optimisation is True
        "title_optimisation_node": returned if previous flag is False and flag_for_title_optimisation is True
        "meta_description_optimisation_node": returned if previous flags are False and flag_for_meta_desc_optimisation is True
        END: returned if all flags are False, as no further optimisation is required for the article
    """
    content_optimisation_flag = state.get("user_flags")["flag_for_content_optimisation"]
    writing_optimisation_flag = state.get("user_flags")["flag_for_writing_optimisation"]
    title_optimisation_flag = state.get("user_flags")["flag_for_title_optimisation"]
    meta_desc_optimisation_flag = state.get("user_flags")[
        "flag_for_meta_desc_optimisation"
    ]

    if content_optimisation_flag:
        return "content_guidelines_optimisation_node"
    elif writing_optimisation_flag:
        return "writing_guidelines_optimisation_node"
    elif title_optimisation_flag:
        return "title_optimisation_node"
    elif meta_desc_optimisation_flag:
        return "meta_description_optimisation_node"
    else:
        return END


def check_personality_after_readability_optimisation(state):
    """Checks for the personality evaluation from the personality_evaluation_node and determine if a subsequent round of writing optimisation is required."""

    # Extracting has_personality from state
    content_flags = state["article_evaluation"]
    has_personality = content_flags["writing_has_personality"]

    if has_personality:
        # Extracts user flags for title and meta desc optimisation
        title_optimisation_flags = state.get("user_flags")[
            "flag_for_title_optimisation"
        ]
        meta_desc_optimisation_flags = state.get("user_flags")[
            "flag_for_meta_desc_optimisation"
        ]
        
        if title_optimisation_flags:
            # Moves state to title optimisation node if article has been flagged for title optimisation
            return "title_optimisation_node"
        elif meta_desc_optimisation_flags:
            # Moves state to meta desc optimisation node if article has been flagged for meta desc optimisation
            return "meta_description_optimisation_node"
        else:
            # If not other optimisation steps are needed, article optimisation ends.
            return END
        
    else:
        return "writing_guidelines_optimisation_node"


def check_num_of_tries_after_readability_optimisation(state):
    # Extracting the new readability score from state
    optimised_article_output = state.get("optimised_article_output")
    new_readability_score = optimised_article_output["readability_score"]

    # Extracting the number of article rewriting tries
    rewriting_tries = state.get("article_rewriting_tries")

    # Checks if number of rewriting tries > limit. If so, the state stops readability optimisation and moves on to subsequent optimisation nodes.
    if rewriting_tries > REWRITING_TRIES:
        print("Number of writing retries exceeded limit hit")

        # Extracts user flags for title and meta desc optimisation
        title_optimisation_flags = state.get("user_flags")[
            "flag_for_title_optimisation"
        ]
        meta_desc_optimisation_flags = state.get("user_flags")[
            "flag_for_meta_desc_optimisation"
        ]
        
        if title_optimisation_flags:
            # Moves state to title optimisation node if article has been flagged for title optimisation
            return "title_optimisation_node"
        elif meta_desc_optimisation_flags:
            # Moves state to meta desc optimisation node if article has been flagged for meta desc optimisation
            return "meta_description_optimisation_node"
        else:
            # If not other optimisation steps are needed, article optimisation ends.
            return END
        
    elif new_readability_score < 10:
        #If readability score < 10, send for personality evaluation
        print(f"Readability score is now {new_readability_score} and considered readable.")
        return "personality_guidelines_evaluation_node"
    
    else:
        # If rewriting tries < limit and readability score >= 10, sends article for rewrite again
        return "readability_optimisation_node"
    
def check_optimised_titles_length(state):
    """ Checks for the length of each optimised title and ensures that all titles have less than 71 characters and reruns title optimisation again if any title does not have less than 71 characters. 

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "title_optimisation_node": returned if at least one optimised title has more than 71 characters
        "meta_description_optimisation_node": returned if all optimised title's lengths < 71 characters and flag_for_meta_desc_optimisation is True
        END: returned if flag_for_meta_desc_optimisation flag is False, as no further optimisation is required for the article
    """

    # Extracting the optimised titles from state
    optimised_article_output = state.get("optimised_article_output")
    optimised_article_titles = optimised_article_output.get("optimised_article_title")

    # For loop iterating thought all article titles to check if all titles have < 71 char
    for title in optimised_article_titles:
        num_of_char = len(title)
        if num_of_char >= 71:
            print("Optimised titles do not meet the length requirements.")
            return "title_optimisation_node"
        
    # Extracting flag for meta desc optimisation
    meta_desc_optimisation_flags = state.get("user_flags")[
    "flag_for_meta_desc_optimisation"
    ]

    # Checking for meta_desc flag for next step in the graph
    if meta_desc_optimisation_flags:
        return "meta_description_optimisation_node"
    else:
        return END


def check_optimised_meta_descs_length(state):
    """Checks for the length of each optimised meta description and ensures that all optimised meta descriptions have more than 70 characters and less than 160 characters.

    Reruns meta description optimisation again if any title does not have more than 70 characters or has less than 160 characters.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        "meta_description_optimisation_node": returned if at least one optimised title does not have more than 70 characters or has less than 160 characters.
        END: returned if all optimised meta descriptions meet the length requirements."""
    
    # Extracting the optimised meta desc from state
    optimised_article_output = state.get("optimised_article_output")
    optimised_article_meta_desc = optimised_article_output.get("optimised_meta_desc")

    # For loop iterating thought all article meta desc to check if all meta desc have more than 70 characters and has less than 160 characters.
    for meta_desc in optimised_article_meta_desc:
        num_of_char = len(meta_desc)
        if num_of_char <= 70 or num_of_char >= 160:
            print("Optimised meta descriptions do not meet the length requirements.")
            return "meta_description_optimisation_node"
        
    return END

def check_readability_after_writing_optimisation(state):
    """Checks for the readability score of the writing optimised article and determines if a subsequent round of rewriting is required to improve the article readability score."""
    # Extracting the new readability score from state
    optimised_article_output = state.get("optimised_article_output")
    new_readability_score = optimised_article_output["readability_score"]

    if new_readability_score < 10:
        print(
            f"Readability score is now {new_readability_score} and considered readable"
        )
        # Checks if article is flagged for title and meta_desc optimisation
        title_optimisation_flags = state.get("user_flags")[
            "flag_for_title_optimisation"
        ]
        meta_desc_optimisation_flags = state.get("user_flags")[
            "flag_for_meta_desc_optimisation"
        ]

        if title_optimisation_flags:
            return "title_optimisation_node"
        elif meta_desc_optimisation_flags:
            return "meta_description_optimisation_node"
        else:
            return END

    else:
        # Send article for readability optimisation as it's readability score is >= 10
        return "readability_optimisation_node"

def build_graph():
    # Gets root directory
    ROOT_DIR = get_root_dir()

    # Declaring dictionary with all nodes
    nodes = {
        "researcher_node": researcher_node,
        "compiler_node": compiler_node,
        "content_guidelines_optimisation_node": content_guidelines_optimisation_node,
        "writing_guidelines_optimisation_node": writing_guidelines_optimisation_node,
        "title_optimisation_node": title_optimisation_node,
        "meta_description_optimisation_node": meta_description_optimisation_node,
        "personality_guidelines_evaluation_node": personality_guidelines_evaluation_node,
        "readability_optimisation_node": readability_optimisation_node,
    }

    # Declaring dictionary with all edges
    edges = {
        START: ["researcher_node"],
        "meta_description_optimisation_node": [END],
    }

    # Declaring dictionary with all conditional edges
    # Example element in conditional edge dictionary: {"name of node": (conditional edge function, path map)}
    conditional_edges = {
        "researcher_node": (
            check_for_compiler,
            {
                "compiler_node": "compiler_node",
                "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END:END
            },
        ),
        "compiler_node": (
            decide_next_optimisation_node,
            {
                "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "content_guidelines_optimisation_node": (
            decide_next_optimisation_node,
            {
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "writing_guidelines_optimisation_node": (
            check_readability_after_writing_optimisation,
            {
                "readability_optimisation_node": "readability_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "readability_optimisation_node": (
            check_num_of_tries_after_readability_optimisation,
            {
                "readability_optimisation_node": "readability_optimisation_node",
                "personality_guidelines_evaluation_node": "personality_guidelines_evaluation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "personality_guidelines_evaluation_node": (
            check_personality_after_readability_optimisation,
            {
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END
            },
        ),
        "title_optimisation_node": (
            check_optimised_titles_length,
            {
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
         "meta_description_optimisation_node": (
            check_optimised_meta_descs_length,
            {
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
    }

    app = create_graph(RewritingState, nodes, edges, conditional_edges)

    # Save Graph
    draw_graph(
        app, f"{ROOT_DIR}/article-harmonisation/docs/images/article_rewriting_flow.png"
    )

    return app

if __name__ == "__main__":

    # starting up the respective llm agents
    researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
    compiler_agent = start_llm(MODEL, ROLES.COMPILER)
    meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC, temperature= 0.5)
    title_optimisation_agent = start_llm(MODEL, ROLES.TITLE, temperature= 0.5)
    content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
    writing_optimisation_agent = start_llm(
        MODEL, ROLES.WRITING_OPTIMISATION, temperature=0.6
    )
    personality_evaluation_agent = start_llm(MODEL, ROLES.PERSONALITY_EVALUATION)
    readability_optimisation_agent = start_llm(
        MODEL, ROLES.READABILITY_OPTIMISATION, temperature=0.5
    )

    # Tesitng list with articles to harmonise
    article_list = [
        # "Rubella", # health conditions
        # "How Dangerous Is Rubella?", # health conditions
        # "Weight, BMI and Health Problems" # live health
        # "Does Your Child Need The Influenza Vaccine?" #live-healthy, null, original readability of 13
        # "Smoking Control Programmes" #live-healthy, body care, original readability of 14
        # "Chickenpox: Symptoms and Treatment Options" # diseases-and-conditions, conditions and illnesses, original readability of 11
    ]

    # # This article list contains all articles under group 7 
    # article_list = [
    #     "Common childhood conditions – Gastroenteritis",
    #     "Food Poisoning in Children",
    #     "Stomach Flu in Children"
    # ]


    # This article list contains all articles under group 139
    article_list = [
        "10 Essential Tips for Mental Well-Being",
        "7 Easy Tips for Better Mental Well-being",
        "Achieve Mental Wellness by Practising Mindfulness",
        "Improve Your Mental Well-being by Going Solo",
        "Mental Wellness Is About the Little Habits Too",
        "Positive Mental Well-being—The Foundation for a Flourishing Life"
    ]

    processed_input_articles = concat_headers_to_content(article_list)

    # Opening the excel contents
    optimization_check = pd.ExcelFile("article-harmonisation/data/optimization_checks/Stage 1 user annotation for HPB (Updated).xlsx")
    df = optimization_check.parse('User Annotation (to optimise)')

    num_of_articles_in_excel = len(df)
    
    for article_idx in range(num_of_articles_in_excel):
        # Extracting article contents
        article = df.iloc[article_idx]

        article_title = article["title"]

        processed_input_articles = concat_headers_to_content(article_title)

        print(return_optimisation_flags(article))

        # Dictionary with the various input keys and items
        inputs = {
            "article_rewriting_tries": 0,
            "original_article_inputs": {"article_content": processed_input_articles,
                                        "article_title": article_list},
            "optimised_article_output": {
                "researcher_keypoints": [],
                "article_researcher_counter": 0,
            },
            "user_flags": return_optimisation_flags(article),

            "llm_agents": {
                "researcher_agent": researcher_agent,
                "compiler_agent": compiler_agent,
                "content_optimisation_agent": content_optimisation_agent,
                "writing_optimisation_agent": writing_optimisation_agent,
                "title_optimisation_agent": title_optimisation_agent,
                "meta_desc_optimisation_agent": meta_desc_optimisation_agent,
                "readability_optimisation_agent": readability_optimisation_agent,
                "personality_evaluation_agent": personality_evaluation_agent,
            },
        }

        result = execute_graph(app, inputs)

        # Prints the various checks
        print_checks(result, MODEL)

        print(result)