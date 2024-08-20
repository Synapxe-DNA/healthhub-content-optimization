from typing import TypedDict

from agents.enums import MODELS, ROLES
from agents.models import start_llm
from checks import ChecksState, create_checks_graph
from harmonisation import (
    RewritingState,
    check_for_compiler,
    compiler_node,
    content_guidelines_optimisation_node,
    decide_next_optimisation_node,
    meta_description_optimisation_node,
    researcher_node,
    title_optimisation_node,
    writing_guidelines_optimisation_node,
)
from langgraph.graph import END, START
from utils.formatters import (
    concat_headers_to_content,
    extract_content_for_evaluation,
    get_article_list_indexes,
    get_article_titles,
    print_checks,
)
from utils.graphs import create_graph, draw_graph, execute_graph
from utils.paths import get_root_dir

MODEL = MODELS("azure").name
ROOT_DIR = get_root_dir()


def start_article_evaluation(articles: list, setting: str = "title"):

    app = create_checks_graph(ChecksState)

    # # Save Graph
    # draw_graph(
    #     app,
    #     f"{ROOT_DIR}/article-harmonisation/docs/images/optimisation_checks_flow.png",
    # )

    # Start LLM
    evaluation_agent = start_llm(MODEL, ROLES.EVALUATOR)
    explanation_agent = start_llm(MODEL, ROLES.EXPLAINER)

    # Load data from merged_data.parquet and randomly sample 30 rows
    article_details = extract_content_for_evaluation(articles, setting)

    for i in range(len(article_details)):
        # Set up
        article_id = article_details[i]["id"]
        article_content = article_details[i]["extracted_content_body"]
        article_title = article_details[i]["title"]
        meta_desc = article_details[i]["category_description"]  # meta_desc can be null
        meta_desc = meta_desc if meta_desc is not None else "No meta description"
        article_url = article_details[i]["full_url"]
        content_category = article_details[i]["content_category"]
        article_category_names = article_details[i]["article_category_names"]
        page_views = article_details[i]["page_views"]

        print(f"Checking {article_title} now...")
        # Set up Inputs
        inputs = {
            "article_inputs": {
                "article_id": article_id,
                "article_title": article_title,
                "article_url": article_url,
                "content_category": content_category,
                "article_category_names": article_category_names,
                "page_views": page_views,
                "article_content": article_content,
                "meta_desc": meta_desc,
            },
            "content_flags": {},
            "title_flags": {},
            "meta_flags": {},
            "content_judge": {},
            "title_judge": {},
            "meta_judge": {},
            "llm_agents": {
                "evaluation_agent": evaluation_agent,
                "explanation_agent": explanation_agent,
            },
        }

        response = execute_graph(app, inputs)
        del response["llm_agents"]
    return response


def start_article_harmonisation(stategraph: ChecksState):
    # Declaring dictionary with all nodes
    nodes = {
        "researcher_node": researcher_node,
        "compiler_node": compiler_node,
        "content_guidelines_optimisation_node": content_guidelines_optimisation_node,
        "writing_guidelines_optimisation_node": writing_guidelines_optimisation_node,
        "title_optimisation_node": title_optimisation_node,
        "meta_description_optimisation_node": meta_description_optimisation_node,
    }

    # Declaring dictionary with all edges
    edges = {
        START: ["researcher_node"],
        "content_guidelines_optimisation_node": [
            "writing_guidelines_optimisation_node"
        ],
        "meta_description_optimisation_node": [END],
    }

    # Declaring dictionary with all conditional edges
    # Example element in conditional edge dictionary: {"name of node": (conditional edge function, path map)}
    conditional_edges = {
        "researcher_node": (
            check_for_compiler,
            {
                "researcher_node": "researcher_node",
                "compiler_node": "compiler_node",
                "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
            },
        ),
        "compiler_node": (
            decide_next_optimisation_node,
            {
                "content_guidelines_optimisation_node": "content_guidelines_optimisation_node",
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "writing_guidelines_optimisation_node": (
            decide_next_optimisation_node,
            {
                "title_optimisation_node": "title_optimisation_node",
                "meta_description_optimisation_node": "meta_description_optimisation_node",
                END: END,
            },
        ),
        "title_optimisation_node": (
            decide_next_optimisation_node,
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

    # starting up the respective llm agents
    researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
    compiler_agent = start_llm(MODEL, ROLES.COMPILER)
    meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC)
    title_optimisation_agent = start_llm(MODEL, ROLES.TITLE)
    content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
    writing_optimisation_agent = start_llm(MODEL, ROLES.WRITING_OPTIMISATION)
    readability_evaluation_agent = start_llm(
        MODEL, ROLES.READABILITY_OPTIMISATION, temperature=0.3
    )
    personality_evaluation_agent = start_llm(MODEL, ROLES.PERSONALITY_EVALUATION)
    readability_optimisation_agent = start_llm(
        MODEL, ROLES.READABILITY_OPTIMISATION, temperature=0.5
    )

    if isinstance(stategraph.get("article_inputs")["article_title"], list):
        processed_input_articles = concat_headers_to_content(
            stategraph.get("article_inputs")["article_title"]
        )
    else:
        processed_input_articles = concat_headers_to_content(
            [stategraph.get("article_inputs")["article_title"]]
        )

    for i in processed_input_articles:
        print(i)

    # Dictionary with the variouse input keys and items
    inputs = {
        "article_rewriting_tries": 0,
        "article_evaluation": stategraph,
        "original_article_inputs": {"article_content": processed_input_articles},
        "optimised_article_output": {
            "researcher_keypoints": [],
            "article_researcher_counter": 0,
        },
        "user_flags": {
            "flag_for_content_optimisation": True,
            "flag_for_writing_optimisation": True,
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
            "readability_optimisation_agent": readability_optimisation_agent,
            "readability_evaluation_agent": readability_evaluation_agent,
            "personality_evaluation_agent": personality_evaluation_agent,
        },
    }

    result = execute_graph(app, inputs)

    # Prints the various checks
    print_checks(result, MODEL)

    return result


def main(article_list: list[str], setting: str = "title") -> TypedDict:
    num_of_articles = len(article_list)

    match num_of_articles:
        case 0:
            raise ValueError("You need to have at least 1 article as input")
        case 1:
            evaluation_stategraph = start_article_evaluation(
                articles=article_list, setting=setting
            )
        case _:
            if setting == "title":
                evaluation_stategraph = {
                    "article_inputs": {"article_title": article_list}
                }
            elif setting == "filename":
                articles_idx = get_article_list_indexes(article_list, setting)
                article_titles = get_article_titles(articles_idx)
                evaluation_stategraph = {
                    "article_inputs": {"article_title": article_titles}
                }

    res = start_article_harmonisation(stategraph=evaluation_stategraph)

    return res


if __name__ == "__main__":
    article_list = [
        "Rubella",
        "How Dangerous Is Rubella?",
        # "Outdoor Activities That Make Fitness Fun in Singapore"
    ]
    print(main(article_list))
