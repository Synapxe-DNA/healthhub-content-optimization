from typing import TypedDict

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
from utils.formatters import split_into_list
from utils.graphs import create_graph, draw_graph
from utils.paths import get_root_dir

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
        article_evaluation: stores inputs for article evaluation
        original_article_inputs: stores original article inputs
        optimised_article_output: stores optimised article outputs from optimisation nodes in the graph
        user_flags: stores user flags for various optimisation steps extracted from the excel sheet
        llm_agents: stores the llm agents used by the article harmonisation/optimisation graph
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

    # Extracting all article titles from state.
    original_article_inputs = state.get("original_article_inputs")
    article_titles = original_article_inputs["article_title"]

    # Extracting all original article content
    article_list = original_article_inputs["article_content"]

    # Extracting researcher keypoints. All outputs from the researcher agent will be appended to this list which will be returned at the end of this node.
    keypoints = state.get("optimised_article_output", [])["researcher_keypoints"]

    # Extracting researcher agent from state.
    researcher_agent = state.get("llm_agents")["researcher_agent"]

    # For loop iterating through each article.
    for idx in range(len(article_list)):
        # Extracting the article title
        article_title = article_titles[idx]

        # Extracting the article content
        article = article_list[idx]

        # Extracting additional content to add to the article from state
        additional_content = original_article_inputs.get("additional_input")

        # Print statement indicating the start of the research process for the particular article
        print(
            f"Processing keypoints for article {idx + 1} of {len(article_list)}: {article_title}"
        )

        # Generating the keypoints using the researcher agent
        article_keypoints = researcher_agent.generate_keypoints(article)

        # If statement for adding additional content to the researcher keypoints. It checks if the additional_content is of float type, as an empty cell in Excel returns "nan", which is a float.
        if not isinstance(additional_content, float):
            article_keypoints = researcher_agent.add_additional_content(
                keypoints=article_keypoints, additional_content=additional_content
            )

        # Add the generated keypoints to the keypoints list
        keypoints.append(article_keypoints)

        # Print statement indicating the end of the research process for the particular article
        print(f"Finished processing keypoints for {article_title}")

    # returning the updated researcher keypoints
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
    # Extracting researcher_keypoints from state
    optimised_article_output = state.get("optimised_article_output")
    keypoints = optimised_article_output["researcher_keypoints"]

    # Runs the compiler LLM to compile the keypoints
    compiler_agent = state.get("llm_agents")["compiler_agent"]

    # Runs the compiler agent to compile the input keypoints
    compiled_keypoints = compiler_agent.compile_points(keypoints)

    # Updating  "ocompiled_keypoints" key in the optimised_article_output dictionary with the recently compiled keypoints
    optimised_article_output["compiled_keypoints"] = compiled_keypoints

    # Returning the updated optimised_article_output dictionary
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
    # Extracting optimised_article_output dictionary from the state
    optimised_article_output = state.get("optimised_article_output")

    # Extracting researcher points. Researcher keypoints are used for meta desc optimisation IF the article has not been flagged for article optimisation i.e. there will be no input for the optimise_writing key
    content = optimised_article_output["researcher_keypoints"]

    # Sets content as optimised writing, if it exists
    if "optimised_writing" in optimised_article_output.keys():
        content = optimised_article_output["optimised_writing"]

    # Extracting meta desc feedback from the state
    article_evaluation = state.get("article_evaluation")
    if article_evaluation is None:
        article_evaluation = {}
    meta_desc_feedback = article_evaluation.get("reasons_for_irrelevant_meta_desc", "")

    # Extracting the meta desc optimisation agent from state
    meta_desc_optimisation_agent = state.get("llm_agents")[
        "meta_desc_optimisation_agent"
    ]

    # Obtaining the optimised meta desc from the agent
    optimised_meta_desc = meta_desc_optimisation_agent.optimise_meta_desc(
        content=content, feedback=meta_desc_feedback
    )

    # Splitting the String of optimised article meta desc into a list where each meta desc is an individual item
    optimised_article_meta_desc = split_into_list(
        optimised_meta_desc, NUM_OF_OPTIMISED_META_DESC
    )

    # Updating the "optimised_meta_desc" key in the optimised_article_output dictionary with the new optimised article meta description
    optimised_article_output["optimised_meta_desc"] = optimised_article_meta_desc

    # Extracing the user flags from flags and updating flag_for_meta_desc_optimisation as False to indicate that meta description optimisation has been completed
    user_flags = state.get("user_flags")
    user_flags["flag_for_meta_desc_optimisation"] = False

    # Returning the updated optimised_article_output and user_flags
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
    # Extracting optimised_article_output dictionary from the state
    optimised_article_output = state.get("optimised_article_output")

    # Extracting researcher points. Researcher keypoints are used for title optimisation IF the article has not been flagged for article optimisation i.e. there will be no input for the optimise_writing key
    content = optimised_article_output["researcher_keypoints"]

    # Sets content as optimised writing, if it exists
    if "optimised_writing" in optimised_article_output.keys():
        content = optimised_article_output["optimised_writing"]

    # Extracting article_evaluation dictionary from state
    article_evaluation = state.get("article_evaluation")

    # If statement to check if article_evaluation is None, as the key "article_evaluation" can store a null value
    if article_evaluation is None:
        article_evaluation = {}

    # Extracting title feedback from the state
    title_feedback = article_evaluation.get("reasons_for_irrelevant_title", "")

    # Extracting the title optimisation agent from state
    title_optimisation_agent = state.get("llm_agents")["title_optimisation_agent"]

    # Obtaining the optimised title from the agent
    optimised_article_title = title_optimisation_agent.optimise_title(
        content=content, feedback=title_feedback
    )

    # Splitting the String of optimised article titles into a list where each title is an individual item
    optimised_article_titles = split_into_list(
        optimised_article_title, NUM_OF_OPTIMISED_TITLES
    )

    # Updating "optimised_article_title" key in optimised_article_output dictionary with the new optimised article titles
    optimised_article_output["optimised_article_title"] = optimised_article_titles

    # Extracing the user flags from flags and updating flag_for_title_optimisation as False to indicate that title optimisation has been completed
    user_flags = state.get("user_flags")
    user_flags["flag_for_title_optimisation"] = False

    # Returning the updated optimised_article_output and user_flags
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
    # Extracting optimised_article_output dictionary from state
    optimised_article_output = state.get("optimised_article_output")

    # Setting keypoints as researcher keypoints
    keypoints = optimised_article_output["researcher_keypoints"]

    # If statement checking if there are any inputs in "compiled_keypoints"
    if "compiled_keypoints" in optimised_article_output.keys():
        keypoints = optimised_article_output["compiled_keypoints"]

    # Runing the compiler LLM to compile the keypoints
    content_optimisation_agent = state.get("llm_agents")["content_optimisation_agent"]

    # Extracting the content category of the article(s)
    content_category = state["original_article_inputs"]["content_category"]

    # Extracting the main article content
    main_article_content = state["original_article_inputs"].get(
        "main_article_content", ""
    )

    # Checking for content category of the article(s) and obtaining the optimised content from the agent
    match content_category:
        # If content category is disease and conditions, there is no need for a main_article_content input and vice versa
        case "diseases-and-conditions":
            optimised_content = content_optimisation_agent.optimise_content(keypoints)
        case "live-healthy-articles":
            optimised_content = content_optimisation_agent.optimise_content(
                keypoints, main_article_content
            )

    # Updating the "optimised_content" key in optimised_article_output dictionary with the new optimised content
    optimised_article_output["optimised_content"] = optimised_content

    # Extracting user flag and updating flag_for_content_optimisation to False to indicate that content guidelines optimisation has been completed
    user_flags = state.get("user_flags")
    user_flags["flag_for_content_optimisation"] = False

    # Returning updated optimised_article_output and user_flags
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
        a dictionary with keys "optimise_writing",  "flag_for_writing_optimisation"
            - optimise_writing: a String containing the optimised writing from the writing optimisation LLM
            - flag_for_writing_optimisation: a False boolean value to indicate that the writing optimisation step has been completed
    """

    # Extracting optimised_article_output dictionary from state
    optimised_article_output = state.get("optimised_article_output")

    # Checks if there is any optimised writing in the state. If so, this is a subsequent writing optimisation of the article.
    if (content := optimised_article_output.get("optimised_writing")) is not None:
        pass
    # Elif checks if there is any optimised content in the state. If so, this is the first writing optimisation for article(s) flagged for content optimisation.
    elif (content := optimised_article_output.get("optimised_content")) is not None:
        pass
    # Elif checks if there is any compiled keypoints in the state. If so, this is the first writing optimisation for an article harmonisation process that's not flagged for content optimisation.
    elif (content := optimised_article_output.get("compiled_keypoints")) is not None:
        pass
    # Else set content to be researcher keypoints as all other cases has been passed. This would be the first writing optimisation for an article optimisation process that's not flagged for content optimisation.
    else:
        content = optimised_article_output.get("researcher_keypoints")

    # Extract writing optimisation agent from state
    writing_optimisation_agent = state.get("llm_agents")["writing_optimisation_agent"]

    # Obtaining the optimised writing from the agent
    optimised_writing = writing_optimisation_agent.optimise_writing(content)

    # Extracting user flag and updating flag_for_writing_optimisation to False to indicate that writing guidelines optimisation has been completed
    user_flags = state.get("user_flags")
    user_flags["flag_for_writing_optimisation"] = False

    # Updating the new optimised writing in the state
    optimised_article_output["optimised_writing"] = optimised_writing

    # Calculating the new readability score
    new_readability_score = calculate_readability(optimised_writing)["score"]

    # Updating the state with the new readability score
    optimised_article_output["readability_score"] = new_readability_score

    # Returning the updated optimised_article_output and user_flags
    return {
        "optimised_article_output": optimised_article_output,
        "user_flags": user_flags,
    }


def readability_optimisation_node(state):
    """Creates a readability optimisation node that optimises the writing based on the feedback given.

        This node aims to improve the Hemingway readability score of the optimised article. The process of improving the readability of the article has been broken into 4 prompts, namely:
            1. "cutting out redundant areas"
            2. "shortening sentences"
            3. "breaking into bullet points"
            4. "simplifying complex terms"

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with keys "optimised_content",  "flag_for_content_optimisation"
            - optimised_content: a String containing the optimised content from the readability optimisation LLM
            - article_rewriting_tries: an Integer value storing the number of times the article has undergone the readability optimisation
    """
    # Obtaining the number of rewriting_tries
    rewriting_tries = state.get("article_rewriting_tries", 0) + 1

    # If statement checking if the number of rewriting tries has exceeded the limit. If True, the node returns the updated readability tries without undergoing the readability optimisation process.
    if rewriting_tries > REWRITING_TRIES:
        return {"article_rewriting_tries": rewriting_tries}

    else:
        # Dictionary with keys as the step number and their corresponding action
        readability_optimisation_steps = {
            1: "cutting out redundant areas",
            2: "shortening sentences",
            3: "breaking into bullet points",
            4: "simplifying complex terms",
        }

        # Extracing the readability optimisation agent from the state
        readability_optimisation_agent = state.get("llm_agents")[
            "readability_optimisation_agent"
        ]

        # Extracting the optimised_article_output dictionary
        optimised_article_output = state.get("optimised_article_output")

        print("## Beginning readability optimisation process ##")
        # For loop iterating through each key (step) in readability_optimisation_steps to optimise the readability of the article
        for step_num in range(1, len(readability_optimisation_steps.keys()) + 1):
            # Obtaining the optimised writing from state
            optimised_writing = optimised_article_output.get("optimised_writing")

            # Extracting the appropriate step from the Dictionary
            step = readability_optimisation_steps[step_num]

            # Obtaining the newly optimised article
            optimised_readability_article = (
                readability_optimisation_agent.optimise_readability(
                    content=optimised_writing, step=step
                )
            )

            # Updating state with the newly readability optimised article
            optimised_article_output["optimised_writing"] = (
                optimised_readability_article
            )
        print("## Readability optimisation process completed ##")

        # Calculating the new readability score
        new_readability_score = calculate_readability(optimised_readability_article)[
            "score"
        ]

        # Updating the state with the new readability score
        optimised_article_output["readability_score"] = new_readability_score

        print(
            f"Rewriting Tries: {rewriting_tries}, Readability score after readability optimisation: {new_readability_score}"
        )

        # Returning the updated article_rewriting_tries and optimised_article_output
        return {
            "article_rewriting_tries": rewriting_tries,
            "optimised_article_output": optimised_article_output,
        }


def personality_guidelines_evaluation_node(state):
    """Creates a personality guidelines evaluation node that evaluates the given content based on the voice and personality guidelines from HH content playbook

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a dictionary with the key "article_evaluation"
            - optimised_content: a Boolean value indicating if the readability optimised writing adheres to the personality guide in HH content playbook
    """

    # Obtaining the recently readability optimised writing from state
    optimised_article_output = state.get("optimised_article_output")
    optimised_writing = optimised_article_output.get("optimised_writing")

    # Extracting the personality_evaluation_agent from the state
    personality_evaluation_agent = state.get("llm_agents")[
        "personality_evaluation_agent"
    ]

    # Obtaining the personality evaluation from the agent
    personality_evaluation = personality_evaluation_agent.evaluate_personality(
        content=optimised_writing
    )

    # Obtaining the article_evaluation Dictionary
    article_evaluation = state.get("article_evaluation", {})

    # state.get("article_evaluation") may return null at times, hence it should be assigned to an empty dictionary
    if not article_evaluation:
        article_evaluation = {}

    # Updating article_evaluation with the updated personality_evaluation flags
    article_evaluation["writing_has_personality"] = personality_evaluation

    # Returning the updated article_evaluation Dictionary to state
    return {
        "article_evaluation": article_evaluation,
    }


# Conditional edge functions
def check_for_compiler(state):
    """Determines if the state should move on to the compiler node for harmonisation, or other article optimisation nodes.

    This function directs the graph state to these nodes based on their respective conditions:
        - "compiler_node": returned if >1 items in article_content list
        - "content_guidelines_optimisation_node": returned if only 1 item in article_content list and user has flagged for content optimisation
        - "writing_guidelines_optimisation_node": returned if the previous conditions are False and user has flagged for writing optimisation
        - "title_optimisation_flag": returned if the previous conditions are False and user has flagged for title optimisation
        - "meta_desc_optimisation_flag": returned if the previous conditions are False and user has flagged for meta description optimisation
        - END: returned if all previous conditions are False

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String from one of the following:
            - "compiler_node": a String that will direct the state to the compiler node
            - "content_guidelines_optimisation_node": a String that will direct the state to the content guidelines optimisation node
            - "writing_guidelines_optimisation_node": a String that will direct the state to the writing guidelines optimisation node
            - "title_optimisation_flag": a String that will direct the state to the title optimisation node
            - "meta_desc_optimisation_flag": a String that will direct the state to the meta desc optimisation node
            - END: a String that will lead the state to the graph end state
    """
    # Extracting the content of all articles from state.
    article_content = state.get("original_article_inputs")["article_content"]

    # Extracting the user flags for various optimisation steps
    user_flags = state.get("user_flags")
    content_optimisation_flag = user_flags["flag_for_content_optimisation"]
    writing_optimisation_flag = user_flags["flag_for_writing_optimisation"]
    title_optimisation_flag = user_flags["flag_for_title_optimisation"]
    meta_desc_optimisation_flag = state.get("user_flags")[
        "flag_for_meta_desc_optimisation"
    ]

    # If statement checking if there are more than 1 item in the article_content list. If True, this means that this is an article harmonisation flow and the state should be sent to the compiler node.
    if len(article_content) < 2:
        # If statements checking for each optimisation flag and sending the state to the respective optimisation node if True
        # Directs state to the content guidelines optimisation node if article is flagged for content optimisation
        if content_optimisation_flag:
            return "content_guidelines_optimisation_node"
        # Directs state to the writing guidelines optimisation node if article is flagged for writing optimisation
        elif writing_optimisation_flag:
            return "writing_guidelines_optimisation_node"
        # Directs state to the title optimisation node if article is flagged for title optimisation
        elif title_optimisation_flag:
            return "title_optimisation_node"
        # Directs state to the meta description optimisation node if article is flagged for meta description optimisation
        elif meta_desc_optimisation_flag:
            return "meta_description_optimisation_node"
        else:
            return END
    else:
        # sending the state to compiler node
        return "compiler_node"


def decide_next_optimisation_node(state):
    """Checks user flags for content optimisation, title optimisation and meta description in state, and returning the appropriate node depending on the stored boolean values of each flag.

    This function directs the graph state to these nodes based on their respective conditions:
        - "content_guidelines_optimisation_node": returned if flag_for_content_optimisation is True
        - "writing_guidelines_optimisation_node": returned if the previous flag is False and flag_for_writing_optimisation is True
        - "title_optimisation_node": returned if previous flags are False and flag_for_title_optimisation is True
        - "meta_description_optimisation_node": returned if previous flags are False and flag_for_meta_desc_optimisation is True
        - END: returned if all flags are False, as no further optimisation is required for the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "content_guidelines_optimisation_node": a String directing the graph state to the content guidelines optimisation node
            - "writing_guidelines_optimisation_node": a String directing the graph state to the writing guidelines optimisation node
            - "title_optimisation_node": a String directing the graph state to the title optimisation node
            - "meta_description_optimisation_node": a String directing the graph state to the meta description optimisation node
            - END: a String directing the state to the end state
    """
    # Extracting the user flags for various optimisation steps
    user_flags = state.get("user_flags")
    content_optimisation_flag = user_flags["flag_for_content_optimisation"]
    writing_optimisation_flag = user_flags["flag_for_writing_optimisation"]
    title_optimisation_flag = user_flags["flag_for_title_optimisation"]
    meta_desc_optimisation_flag = state.get("user_flags")[
        "flag_for_meta_desc_optimisation"
    ]

    # If statement checking for the various user flags to determine which String to return
    # Directs state to the content guidelines optimisation node if article is flagged for content optimisation
    if content_optimisation_flag:
        return "content_guidelines_optimisation_node"
    # Directs state to the writing guidelines optimisation node if article is flagged for writing optimisation
    elif writing_optimisation_flag:
        return "writing_guidelines_optimisation_node"
    # Directs state to the title optimisation node if article is flagged for title optimisation
    elif title_optimisation_flag:
        return "title_optimisation_node"
    # Directs state to the meta description optimisation node if article is flagged for meta description optimisation
    elif meta_desc_optimisation_flag:
        return "meta_description_optimisation_node"
    else:
        return END


def check_personality_after_personality_evaluation(state):
    """Checks for the personality evaluation of the readability optimised article to determine if a subsequent round of writing optimisation is required.

    If personality evaluation has failed, then state will be directed to writing_guidelines_optimisation_node for another round of writing guidelines optimisation.

    This function directs the graph state to these nodes based on their respective conditions:
        - "writing_guidelines_optimisation_node": returned if readability optimised article does not meet the HH guidelines
        - "title_optimisation_node": returned if readability optimised article meets the HH guidelines and flag_for_title_optimisation is True
        - "meta_description_optimisation_node": returned if previous flag is False and flag_for_meta_desc_optimisation is True
        - END: returned if both flags are False, as no further optimisation is required for the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "writing_guidelines_optimisation_node": a String directing the graph state to the writing guidelines optimisation node
            - "title_optimisation_node": a String directing the graph state to the title optimisation node
            - "meta_description_optimisation_node": a String directing the graph state to the meta description optimisation node
            - END: a String directing the state to the end state
    """

    # Extracting has_personality from state. has_personality is True if writing follows personality guidelines and False otherwise
    content_flags = state["article_evaluation"]
    has_personality = content_flags["writing_has_personality"]

    if has_personality:
        # Extracts user flags for title and meta desc optimisation
        user_flags = state.get("user_flags")
        title_optimisation_flag = user_flags["flag_for_title_optimisation"]
        meta_desc_optimisation_flag = state.get("user_flags")[
            "flag_for_meta_desc_optimisation"
        ]

        if title_optimisation_flag:
            # Directs state to title optimisation node if article has been flagged for title optimisation
            return "title_optimisation_node"
        elif meta_desc_optimisation_flag:
            # Directs state to meta desc optimisation node if article has been flagged for meta desc optimisation
            return "meta_description_optimisation_node"
        else:
            # If not other optimisation steps are needed, article optimisation ends.
            return END

    else:
        # Directs state to writing guidelines optimisation node if not has_personality
        return "writing_guidelines_optimisation_node"


def check_num_of_tries_after_readability_optimisation(state):
    """Checks the number of rewriting tries after readability optimisation to determine which node to direct the state to. This function ensures that the article will be repeatedly rewritten until the readability of the article is < 10, whilst not exceeding the limit of rewriting tries.

    This function directs the graph state to these nodes based on their respective conditions:
        - "personality_guidelines_evaluation_node": returned if current number of readability tries exceeds the limit OR if new readability score < 10
        - "readability_optimisation_node": returned if new readability score >= 10 and current rewriting tries < limit

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "personality_guidelines_evaluation_node": a String directing the state to the personality guidelines evaluation node
            - "readability_optimisation_node": a String directing the state to the readability optimisation node
    """

    # Extracting the new readability score from state
    optimised_article_output = state.get("optimised_article_output")
    new_readability_score = optimised_article_output["readability_score"]

    # Extracting the number of article rewriting tries
    rewriting_tries = state.get("article_rewriting_tries")

    # Checks if number of rewriting tries > limit and if new_readability score < 10. If so, the state exits the readability optimisation loop and moves on to subsequent optimisation nodes.
    if rewriting_tries > REWRITING_TRIES or new_readability_score < 10:
        if rewriting_tries > REWRITING_TRIES:
            print("Number of writing retries exceeded limit hit")
        elif new_readability_score < 10:
            print(
                f"Readability score is now {new_readability_score} and considered readable."
            )
        return "personality_guidelines_evaluation_node"

    else:
        # If rewriting tries < limit and readability score >= 10, sends article for rewrite again
        return "readability_optimisation_node"


def check_optimised_titles_length(state):
    """Checks for the length of each optimised title and ensures that all titles have less than 71 characters and reruns title optimisation again if any title does not have less than 71 characters.

    This function directs the graph state to these nodes based on their respective conditions:
        - "title_optimisation_node": returned if at least one optimised title has more than 71 characters
        - "meta_description_optimisation_node": returned if all optimised title's lengths < 71 characters and flag_for_meta_desc_optimisation is True
        - END: returned if flag_for_meta_desc_optimisation flag is False, as no further optimisation is required for the article

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "title_optimisation_node": a String that directs that state to the title optimisation node
            - "meta_description_optimisation_node": a String that directs the state to the meta description optimisation node
            - END: a String directing the state to the end state
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

    Reruns meta description optimisation again if any meta description does not have more than 70 characters or has less than 160 characters.

    This function directs the graph state to these nodes based on their respective conditions:
        - "meta_description_optimisation_node": returned if at least one optimised meta description does not have more than 70 characters or has less than 160 characters.
        - END: returned if all optimised meta descriptions meet the length requirements.

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "meta_description_optimisation_node": a String that directs the state to the meta description optimisation node
            - END: a String directing the state to the end state
    """

    # Extracting the optimised meta desc from state
    optimised_article_output = state.get("optimised_article_output")
    optimised_article_meta_desc = optimised_article_output.get("optimised_meta_desc")

    # For loop iterating thought all article meta desc to check if all meta desc have more than 70 characters and has less than 160 characters.
    for meta_desc in optimised_article_meta_desc:
        num_of_char = len(meta_desc)
        # If statement checking the meta description with the length requirements
        if num_of_char <= 70 or num_of_char >= 160:
            print("Optimised meta descriptions do not meet the length requirements.")
            return "meta_description_optimisation_node"
    return END


def check_readability_after_writing_optimisation(state):
    """Checks for the readability score of the writing optimised article and determines if a subsequent round of rewriting is required to improve the article readability score.

    Otherwise, the graph state will directed to other nodes.

    This function directs the graph state to these nodes based on their respective conditions:
        - "readability_optimisation_node": returned if new readability score >= 10 and current rewriting tries < limit
        - "title_optimisation_node": returned if any of the previous conditions are False and if user has flagged the article for title optimisation
        - "meta_description_optimisation_node": returned if any of the previous conditions are False and if user has flagged the article for meta description optimisation
        - END: returned if any of the above conditions are False and sends the graph to the end state

    Args:
        state: a dictionary storing relevant attributes as keys and content as the respective items.

    Returns:
        a String that can be one of the following:
            - "readability_optimisation_node": a String directing the state to the readability optimisation node
            - "title_optimisation_node": a String that directs that state to the title optimisation node
            - "meta_description_optimisation_node": a String that directs the state to the meta description optimisation node
            - END: a String directing the state to the end state
    """
    # Extracting the new readability score from state
    optimised_article_output = state.get("optimised_article_output")
    new_readability_score = optimised_article_output["readability_score"]

    # Extracting the number of article rewriting tries
    rewriting_tries = state.get("article_rewriting_tries")

    # If statement checking for new readability score and the number of rewriting tries
    if new_readability_score < 10 or rewriting_tries >= REWRITING_TRIES:

        # If statement to print out the appropriate statements for checking
        if new_readability_score < 10:
            print(
                f"Readability score is now {new_readability_score} and considered readable."
            )

        else:
            print("Number of writing retries exceeded limit hit.")

        # Extracting title optimisation flag from state
        title_optimisation_flags = state.get("user_flags")[
            "flag_for_title_optimisation"
        ]

        # Extracting meta description optimisation flag from state
        meta_desc_optimisation_flags = state.get("user_flags")[
            "flag_for_meta_desc_optimisation"
        ]

        # If statement checking if article is flagged for title optimisation and returning "title_optimisation_node"
        if title_optimisation_flags:
            return "title_optimisation_node"

        # elif statement checking if article is flagged for meta description optimisation and returning "meta_description_optimisation_node"
        elif meta_desc_optimisation_flags:
            return "meta_description_optimisation_node"

        # If both conditions above are False, return END
        else:
            return END

    else:
        # Send article for readability optimisation as it's readability score is >= 10 and rewriting tries < limit
        return "readability_optimisation_node"


def build_graph():
    """Creates and compiles a StateGraph object based on the provided schema, nodes, and edges using create_graph().

    nodes, edges, conditional_edges dictionary for creating a harmonisation flow are defined here and used to create the harmonisation graph.

    Returns:
        CompiledGraph: The compiled StateGraph object ready for execution.
    """
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
        # Direct edge from START of graph to researcher_node
        START: ["researcher_node"],
    }

    # Declaring dictionary with all conditional edges
    # Example element in conditional edge dictionary: {"name of node": (conditional edge function, path map)}
    conditional_edges = {
        # Conditional edge from researcher_node that checks if state should move to compiler node or other optimisation nodes
        "researcher_node": (
            check_for_compiler,
            {
                "compiler_node": "compiler_node",
                "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        # Conditonal edge from compiler_node that checks the user flags to determine which optimisation node to direct the state to
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
        # Conditonal edge from content_guidelines_optimisation_node that checks the user flags to determine which optimisation node to direct the state to
        "content_guidelines_optimisation_node": (
            decide_next_optimisation_node,
            {
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        # Conditional edge from writing_guidelines_optimisation_node that checks the readability score of the article and determines if the state moves to the readability optimisation node again or to other optimisation nodes
        "writing_guidelines_optimisation_node": (
            check_readability_after_writing_optimisation,
            {
                "readability_optimisation_node": "readability_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        # Conditional edge from readability_optimisation_node that checks the number of rewriting tries after readability optimisation to determine which optimisatio node to direct the state to.
        "readability_optimisation_node": (
            check_num_of_tries_after_readability_optimisation,
            {
                "readability_optimisation_node": "readability_optimisation_node",
                "personality_guidelines_evaluation_node": "personality_guidelines_evaluation_node",
            },
        ),
        # Conditional edge from personality_guidelines_evaluation_node that checks the personality evaluation of a rewritten article to determine whether to direct the state for another round of writing guidelines optimisation or to other optimisation nodes.
        "personality_guidelines_evaluation_node": (
            check_personality_after_personality_evaluation,
            {
                "writing_guidelines_optimisation_node": "writing_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        # Conditional edge from title_optimisation_node that checks for the length of each optimised title and determines if the state should be directed for another round of title optimisation rewrite or to other nodes.
        "title_optimisation_node": (
            check_optimised_titles_length,
            {
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        # Conditional edge from meta_description_optimisation_node that checks for the length of each optimisation meta description that determines if the state should be directed for another round of meta description optimisation or to end the harmonisation process.
        "meta_description_optimisation_node": (
            check_optimised_meta_descs_length,
            {
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
    }

    # Creating the GraphState object using the defined nodes, edges, conditional_edges
    app = create_graph(RewritingState, nodes, edges, conditional_edges)

    # Saving the diagram of the graph
    draw_graph(
        app, f"{ROOT_DIR}/article-harmonisation/docs/images/article_rewriting_flow.png"
    )

    return app
