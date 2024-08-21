import pandas as pd
from agents.enums import ROLES
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

        article_inputs = [
            article_group_number,  # Group Number
            article_sub_group,  # Subgroup
            article_group_description,  # Group Description
            str(article_sub_group_ids),  # Article ids
            str(article_sub_group_urls),  # Article urls
            # Article title optimisation
            result["optimised_article_output"]["optimised_article_title"][
                0
            ],  # Optimised title 1
            result["optimised_article_output"]["optimised_article_title"][
                1
            ],  # Optimised title 2
            result["optimised_article_output"]["optimised_article_title"][
                2
            ],  # Optimised title 3
            None,  # Title chosen (user to choose 1 from: Title 1, Title 2, Title 3 or ‘Write your own’)
            None,  # Optional: Title written by user (free text for user to add only if ‘Write your own’ is chosen)
            # Article meta desc optimisation
            result["optimised_article_output"]["optimised_meta_desc"][
                0
            ],  # Optimised meta desc 1
            result["optimised_article_output"]["optimised_meta_desc"][
                1
            ],  # Optimised meta desc 2
            result["optimised_article_output"]["optimised_meta_desc"][
                2
            ],  # Optimised meta desc 3
            None,  # Meta Description chosen (user to choose 1 from: Meta Description 1, Meta Description 2, Meta Description 3 or ‘Write your own’)
            None,  # Optional: meta description written by user (free text for user to add only if ‘Write your own’ is chosen)
            # Article writing optimisation
            result["optimised_article_output"][
                "optimised_writing"
            ],  # Rewritten article content (should be a link)
            None,  # Optimised changes summary (could be nil)
            None,  # User approval for optimised article (Y/N)
            None,  # User attached updated article
        ]

        store_optimised_outputs(
            USER_ANNOTATION, HARMONISATION_SHEET_NAME, article_inputs
        )


if __name__ == "__main__":
    # starting up the respective llm agents
    researcher_agent = start_llm(MODEL, ROLES.RESEARCHER)
    compiler_agent = start_llm(MODEL, ROLES.COMPILER)
    meta_desc_optimisation_agent = start_llm(MODEL, ROLES.META_DESC, temperature=0.5)
    title_optimisation_agent = start_llm(MODEL, ROLES.TITLE, temperature=0.5)
    content_optimisation_agent = start_llm(MODEL, ROLES.CONTENT_OPTIMISATION)
    writing_optimisation_agent = start_llm(
        MODEL, ROLES.WRITING_OPTIMISATION, temperature=0.6
    )
    personality_evaluation_agent = start_llm(MODEL, ROLES.PERSONALITY_EVALUATION)
    readability_optimisation_agent = start_llm(
        MODEL, ROLES.READABILITY_OPTIMISATION, temperature=0.5
    )

    app = build_graph()

    optimise_articles(app)
