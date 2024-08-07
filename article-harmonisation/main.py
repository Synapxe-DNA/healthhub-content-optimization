from agents.enums import MODELS, ROLES
from agents.models import start_llm
from checks import (
    ChecksState,
    content_evaluation_llm_node,
    content_evaluation_rules_node,
    content_explanation_node,
    meta_desc_evaluation_llm_node,
    meta_desc_evaluation_rules_node,
    title_evaluation_llm_node,
    title_evaluation_rules_node,
)
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
    print_checks,
)
from utils.graphs import create_graph, draw_graph, execute_graph
from utils.paths import get_root_dir

MODEL = MODELS("azure").name
ROOT_DIR = get_root_dir()


def start_article_evaluation(articles: list):

    nodes = {
        "content_evaluation_rules_node": content_evaluation_rules_node,
        "content_explanation_node": content_explanation_node,
        "content_evaluation_llm_node": content_evaluation_llm_node,
        "title_evaluation_rules_node": title_evaluation_rules_node,
        "title_evaluation_llm_node": title_evaluation_llm_node,
        "meta_desc_evaluation_rules_node": meta_desc_evaluation_rules_node,
        "meta_desc_evaluation_llm_node": meta_desc_evaluation_llm_node,
    }

    edges = {
        START: [
            "content_evaluation_rules_node",
            "title_evaluation_rules_node",
            "meta_desc_evaluation_rules_node",
        ],
        "content_evaluation_rules_node": ["content_explanation_node"],
        "content_explanation_node": ["content_evaluation_llm_node"],
        "content_evaluation_llm_node": [END],
        "title_evaluation_rules_node": ["title_evaluation_llm_node"],
        "title_evaluation_llm_node": [END],
        "meta_desc_evaluation_rules_node": ["meta_desc_evaluation_llm_node"],
        "meta_desc_evaluation_llm_node": [END],
    }

    app = create_graph(ChecksState, nodes, edges)

    # Save Graph
    draw_graph(
        app,
        f"{ROOT_DIR}/article-harmonisation/docs/images/optimisation_checks_flow.png",
    )

    # Start LLM
    evaluation_agent = start_llm(MODEL, ROLES.EVALUATOR)
    explanation_agent = start_llm(MODEL, ROLES.EXPLAINER)

    # Load data from merged_data.parquet and randomly sample 30 rows
    article_details = extract_content_for_evaluation(articles)

    for i in range(len(article_details)):
        # Set up
        article_content = article_details[i]["extracted_content_body"]
        article_title = article_details[i]["title"]
        meta_desc = article_details[i]["category_description"]  # meta_desc can be null

        print(f"Checking {article_title} now...")
        # Set up Inputs
        inputs = {
            "article_content": article_content,
            "article_title": article_title,
            "meta_desc": meta_desc,
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

    if isinstance(stategraph.get("article_title"), list):
        processed_input_articles = concat_headers_to_content(
            stategraph.get("article_title")
        )
    else:
        processed_input_articles = concat_headers_to_content(
            [stategraph.get("article_title")]
        )

    for i in processed_input_articles:
        print(i)

    # Dictionary with the variouse input keys and items
    inputs = {
        "article_evaluation": stategraph,
        "original_article_content": {"article_content": processed_input_articles},
        "optimised_article_output": {
            "researcher_keypoints": [],
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


if __name__ == "__main__":
    article_list = [
        "Rubella",
        "How Dangerous Is Rubella?",
        # "Outdoor Activities That Make Fitness Fun in Singapore"
    ]
    num_of_articles = len(article_list)
    match num_of_articles:
        case 0:
            raise ValueError("You need to have at least 1 article as input")
        case 1:
            evaluation_stategraph = start_article_evaluation(articles=article_list)
        case _:
            evaluation_stategraph = {"article_title": article_list}

    start_article_harmonisation(stategraph=evaluation_stategraph)
