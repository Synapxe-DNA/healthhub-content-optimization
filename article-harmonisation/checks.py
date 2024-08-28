import sys
import time
import traceback
from datetime import datetime
from glob import glob
from typing import Annotated, Optional, TypedDict

import pandas as pd
from agents.enums import ROLES
from agents.models import start_llm
from config import settings
from langgraph.graph import END, START
from langgraph.graph.graph import CompiledGraph
from states.definitions import (
    ArticleInputs,
    ChecksAgents,
    ContentFlags,
    ContentJudge,
    MetaFlags,
    MetaJudge,
    SkipLLMEvals,
    TitleFlags,
    TitleJudge,
)
from tqdm import tqdm
from utils.evaluations import calculate_readability
from utils.formatters import format_checks_outputs
from utils.graphs import create_graph, execute_graph
from utils.paths import get_root_dir
from utils.reducers import merge_dict

# Declaring maximum new tokens
MAX_NEW_TOKENS = settings.MAX_NEW_TOKENS

# Declaring model to use
MODEL = settings.MODEL_NAME


class ChecksState(TypedDict):
    """
    A TypedDict class that encapsulates various keys relevant to the project, including article inputs, flags, judges, and LLM agents.

    Attributes:
        article_inputs (ArticleInputs): Contains inputs related to the article being evaluated.
        skip_llm_evaluations (SkipLLMEvals): Contains input flags whether to skip LLM-based evaluations
        content_flags (Annotated[ContentFlags, merge_dict]): Flags based on content analysis using rule-based/statistical methods.
        title_flags (Annotated[TitleFlags, merge_dict]): Flags based on title analysis using rule-based/statistical methods.
        meta_flags (Annotated[MetaFlags, merge_dict]): Flags based on meta description analysis using rule-based/statistical methods.
        content_judge (Annotated[ContentJudge, merge_dict]): Explanations and decisions related to content quality.
        title_judge (Annotated[TitleJudge, merge_dict]): Explanations and decisions related to title quality.
        meta_judge (Annotated[MetaJudge, merge_dict]): Explanations and decisions related to meta description quality.
        llm_agents (ChecksAgents): Agents responsible for executing checks and evaluations.
    """

    # Article Inputs
    article_inputs: ArticleInputs

    # Skip LLM evaluations
    skip_llm_evaluations: SkipLLMEvals

    # Flags for rule-based/statistical-based methods
    content_flags: Annotated[ContentFlags, merge_dict]
    title_flags: Annotated[TitleFlags, merge_dict]
    meta_flags: Annotated[MetaFlags, merge_dict]

    # Explanations for various criteria
    content_judge: Annotated[ContentJudge, merge_dict]
    title_judge: Annotated[TitleJudge, merge_dict]
    meta_judge: Annotated[MetaJudge, merge_dict]

    # Agents responsible for the checks
    llm_agents: ChecksAgents


def content_evaluation_rules_node(state: ChecksState) -> dict:
    """
    Perform Rule-based evaluations on the article content

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated content flags dictionary containing the decision to optimise the article content
    """

    article_content = state.get("article_inputs")["article_content"]
    content_category = state.get("article_inputs")["content_category"]
    content_flags = state.get("content_flags", {})

    # Check readability - Hemmingway Metric
    metric = calculate_readability(article_content, "hemmingway")
    score = metric.get("score", -1)

    # NOTE: Exceptions must be handled to prevent the program from being prematurely terminated
    # Article is deemed as unreadable if the score is at least 10
    if score <= 0:
        raise ValueError("The readability score must be greater than 0.")
    elif score >= 10:
        content_flags["is_unreadable"] = True
    else:
        content_flags["is_unreadable"] = False

    content_flags["readability_score"] = score

    # Check for insufficient content - Less than 300 - 400 words is considered too brief to adequately cover a topic unless it's a very specific and narrow subject
    # Threshold is set at the 25th percentile - Flag articles below 25th percentile for each content category
    word_count_threshold_dict = {
        "cost-and-financing": 267,
        "live-healthy-articles": 413,
        "diseases-and-conditions": 368,
        "medical-care-and-facilities": 202,
        "support-group-and-others": 213,
    }
    word_count = len(article_content.split())
    # Flag articles based on the provided threshold. Otherwise, flag articles below 300 words
    threshold = word_count_threshold_dict.get(content_category, 300)
    if word_count < threshold:
        content_flags["low_word_count"] = True
    else:
        content_flags["low_word_count"] = False

    return {"content_flags": content_flags}


def content_explanation_node(state: ChecksState) -> dict:
    """
    Provide explanations if poor readability is detected.

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated content judge dictionary containing explanations for content quality.
    """

    # Check if LLM evaluation is skipped
    skip_llm = state.get("skip_llm_evaluations", {}).get("decision", False)
    if skip_llm:
        return

    # Extract article content, content flags and content judge from the state
    article_content = state.get("article_inputs")["article_content"]
    content_flags = state.get("content_flags", {})
    content_judge = state.get("content_judge", {})

    # Explain Poor Readability based on Readability Matrix - Low Priority
    readability = content_flags.get("is_unreadable", False)

    if readability:
        # If readability is poor, use the explanation agent to evaluate and explain the issue
        explanation_agent = state.get("llm_agents")["explanation_agent"]
        readability_explanation = explanation_agent.evaluate_content(
            article_content, choice="readability"
        )
        content_judge["readability"] = readability_explanation

    return {"content_judge": content_judge}


def content_evaluation_llm_node(state: ChecksState) -> dict:
    """
    Provide LLM-based evaluations for content structure/writing style

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated content judge dictionary containing decisions and explanations for content quality.

    Note:
        Writing style optimisation has been removed as all articles are being flagged as true. Further refinement is required.
        For now, the writing style evaluation has been commented out upon request. However, this may change in the future.
    """

    # Check if LLM evaluation is skipped
    skip_llm = state.get("skip_llm_evaluations", {}).get("decision", False)
    if skip_llm:
        return

    # # Extract article content and content judge from the state
    # article_content = state.get("article_inputs")["article_content"]
    # content_judge = state.get("content_judge", {})
    # content_evaluation_agent = state.get("llm_agents")["evaluation_agent"]
    #
    # # Check for poor content structure - Refer to `return_structure_evaluation_prompt` function in agents/prompts.py
    # content_structure_eval = content_evaluation_agent.evaluate_content(
    #     article_content, choice="structure"
    # )
    # content_judge["structure"] = content_structure_eval
    #
    # return {"content_judge": content_judge}
    pass


def title_evaluation_rules_node(state: ChecksState) -> dict:
    """
    Perform Rule-based evaluations on the article title

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated title flags dictionary containing the decision to optimise the article title
    """

    # Extract article title and title flags from the state
    article_title = state.get("article_inputs")["article_title"]
    title_flags = state.get("title_flags", {})

    # Check if article title exceeds character count - Exceeds 70 Characters
    char_count = len(article_title)
    if char_count <= 0:
        raise ValueError("The title character count must be greater than 0.")
    elif char_count > 70:
        title_flags["long_title"] = True
    else:
        title_flags["long_title"] = False

    return {"title_flags": title_flags}


def title_evaluation_llm_node(state: ChecksState) -> dict:
    """
    Provide LLM-based evaluations for irrelevant title

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated title judge dictionary containing decisions and explanations regarding title relevance
    """

    # Check if LLM evaluation is skipped
    skip_llm = state.get("skip_llm_evaluations", {}).get("decision", False)
    if skip_llm:
        return

    # Extract article title, article content and title judge from the state
    article_title = state.get("article_inputs")["article_title"]
    article_content = state.get("article_inputs")["article_content"]
    title_judge = state.get("title_judge", {})

    # Check for irrelevant Page Title - Evaluate against the article content
    title_evaluation_agent = state.get("llm_agents")["evaluation_agent"]
    title_evaluation = title_evaluation_agent.evaluate_title(
        article_title, article_content
    )
    title_judge["title"] = title_evaluation

    return {"title_judge": title_judge}


def meta_desc_evaluation_rules_node(state: ChecksState) -> dict:
    """
    Perform Rule-based evaluations on the article meta description

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated meta flags dictionary containing the decision to optimise the article meta description
    """

    # Extract article meta description and meta flags from the state
    meta_desc = state.get("article_inputs")["meta_desc"]
    meta_flags = state.get("meta_flags", {})

    # Check if Meta Description Char Count is out of bounds - Less than 70 or More than 160 characters
    char_count = len(meta_desc)
    if char_count <= 0:
        raise ValueError("The meta description character count must be greater than 0.")
    elif 70 <= char_count <= 160:
        meta_flags["not_within_char_count"] = False
    else:
        meta_flags["not_within_char_count"] = True

    return {"meta_flags": meta_flags}


def meta_desc_evaluation_llm_node(state: ChecksState) -> dict:
    """
    Provide LLM-based evaluations for irrelevant meta description

    Args:
        state (ChecksState): The current state of checks, including article inputs, flags, and LLM agents.

    Returns:
        dict: Updated meta judge dictionary containing decisions and explanations regarding meta description relevance
    """

    # Check if LLM evaluation is skipped
    skip_llm = state.get("skip_llm_evaluations", {}).get("decision", False)
    if skip_llm:
        return

    # Extract article meta description, article content and meta judge from the state
    meta_desc = state.get("article_inputs")["meta_desc"]
    article_content = state.get("article_inputs")["article_content"]
    meta_judge = state.get("meta_judge", {})

    # Check for irrelevant Meta Description - Evaluate against the article content
    meta_evaluation_agent = state.get("llm_agents")["evaluation_agent"]
    meta_evaluation = meta_evaluation_agent.evaluate_meta_description(
        meta_desc, article_content
    )
    meta_judge["meta_desc"] = meta_evaluation

    return {"meta_judge": meta_judge}


def create_checks_graph(state: ChecksState) -> CompiledGraph:
    """
    Creates and compiles a checks graph for evaluating content, title, and meta descriptions using both rule-based and LLM-based nodes.

    Args:
        state (ChecksState): The current state containing article inputs, evaluation flags, and LLM agents.

    Returns:
        CompiledGraph: A compiled graph that represents the evaluation process for content, title, and meta descriptions.
    """

    # Define nodes for different evaluation processes
    nodes = {
        "content_evaluation_rules_node": content_evaluation_rules_node,
        "content_explanation_node": content_explanation_node,
        "content_evaluation_llm_node": content_evaluation_llm_node,
        "title_evaluation_rules_node": title_evaluation_rules_node,
        "title_evaluation_llm_node": title_evaluation_llm_node,
        "meta_desc_evaluation_rules_node": meta_desc_evaluation_rules_node,
        "meta_desc_evaluation_llm_node": meta_desc_evaluation_llm_node,
    }

    # Define edges to establish the flow between nodes
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

    # Create the compiled graph using the provided state, nodes, and edges
    app = create_graph(state, nodes, edges)

    # # Save the graph visualization as an image
    # draw_graph(
    #     app,
    #     f"{ROOT_DIR}/article-harmonisation/docs/images/optimisation_checks_flow.png",
    # )

    return app


def load_evaluation_dataframe(
    full_data_filepath: str, ids_filepath: str
) -> tuple[pd.DataFrame]:
    """
    Load and prepare evaluation dataframe for article harmonisation.

    This function loads the full dataset from a parquet file + article IDs from a csv file, checks for previously evaluated articles,
    and filters the dataframe to include only relevant Health Promotion Board articles that haven't been evaluated yet.

    Args:
        full_data_filepath (str): The path to the parquet file to load the full dataset.
        ids_filepath (str): The path to the parquet file to load the article IDs.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - df_keep: DataFrame of articles to be evaluated
            - df_eval: DataFrame of previously evaluated articles (or None if no evaluations exist)

    Note:
        filepaths variable should match the filepath used to save the generated evaluation dataframe in `save_evaluation_dataframe`
    """

    # Load data from merged_data.parquet
    df = pd.read_parquet(full_data_filepath)

    # Get latest evaluation dataframe
    filepaths = sorted(
        glob(
            f"{ROOT_DIR}/article-harmonisation/data/optimization_checks/agentic_response_*.parquet"
        )
    )
    if len(filepaths) == 0:
        evaluated_article_ids = []
        df_eval = None
    else:
        latest_fpath = filepaths[-1]
        print(f"Loading latest article evaluation dataframe from {latest_fpath}...")
        df_eval = pd.read_parquet(latest_fpath)
        if "article_id" in df_eval.columns:
            evaluated_article_ids = list(df_eval.article_id)
            print(f"Evaluated Article IDs: {evaluated_article_ids}")
        else:
            print(
                "Article ID does not exist in Latest Article Evaluation Dataset. Please remove this file if it is empty."
            )
            print("Evaluating all articles...")
            evaluated_article_ids = []
            df_eval = None

    # Get articles for Optimisation
    df_ids_to_optimise = pd.read_csv(ids_filepath)
    ids_to_optimise = list(df_ids_to_optimise.article_id)

    # Filter for relevant HPB articles
    df_keep = df[~df["to_remove"]]
    df_keep = df_keep[df_keep["pr_name"] == "Health Promotion Board"]
    df_keep = df_keep[
        df_keep["content_category"].isin(
            [
                "cost-and-financing",
                "live-healthy-articles",
                "diseases-and-conditions",
                "medical-care-and-facilities",
                "support-group-and-others",
            ]
        )
    ]
    # Keep articles of interest that need to be evaluated based on provided user annotations
    df_keep = df_keep[df_keep["id"].isin(ids_to_optimise)]

    # Filter out articles that have already been evaluated
    df_keep = df_keep[~df_keep["id"].isin(evaluated_article_ids)]
    ids_to_evaluate = list(df_keep.id)
    print(
        f"Total number of articles to evaluate: {len(ids_to_evaluate)}\nArticle IDs: {ids_to_evaluate}",
        end="\n\n",
    )

    return df_keep, df_eval


def save_evaluation_dataframe(
    records_list: list[dict], df_eval: Optional[pd.DataFrame]
) -> None:
    """
    Save evaluation results to a parquet file.

    This function takes a list of evaluation records and an optional existing evaluation DataFrame, combines them if applicable,
    and saves the result to a new parquet file with a timestamp in the filename.

    Args:
        records_list (list[dict]): A list of dictionaries containing evaluation records.
        df_eval (pd.DataFrame, Optional): An optional pandas DataFrame containing existing evaluation data.
            If provided, it will be concatenated with the new records.

    Returns:
        None

    Note:
        The columns stated in df_store must exist. Refer to `format_checks_outputs` in utils/formatters.py
    """

    # Generate current timestamp for the filename
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    # Convert the list of records to a DataFrame
    df_save = pd.DataFrame.from_records(records_list)

    # Concatenate with existing evaluation data if provided
    if df_eval is not None:
        df_store = pd.concat([df_eval, df_save], ignore_index=True)
    else:
        df_store = df_save

    # Save the combined DataFrame to a parquet file (Saved as agentic_response_*.parquet)
    df_store.to_parquet(
        f"{ROOT_DIR}/article-harmonisation/data/optimization_checks/agentic_response_{current_datetime}.parquet",
        index=False,
    )
    print("Results saved!")


if __name__ == "__main__":
    # Get root directory (Set at healthhub-content-optimization)
    ROOT_DIR = get_root_dir()

    # Get dataframe of articles to be evaluated
    merged_data_filepath = f"{ROOT_DIR}/article-harmonisation/data/merged_data.parquet"
    ids_to_optimise_filepath = (
        f"{ROOT_DIR}/article-harmonisation/data/ids_for_optimisation.csv"
    )
    df_keep, df_evaluated = load_evaluation_dataframe(
        merged_data_filepath, ids_to_optimise_filepath
    )

    # Note: n can be adjusted as and when needed.
    # Usually, lower n is useful for generating evaluations in a more stable manner
    df_sample = df_keep.sample(n=df_keep.shape[0], replace=False)  # random_state=42
    print(df_sample.id)

    # Print the total number of articles which the optimisation checks graph is being performed on
    n_samples = df_sample.shape[0]
    print(f"Number of samples: {n_samples}")

    # Compile the Checks graph for Optimisation Checks
    app = create_checks_graph(ChecksState)

    # Initialise the LLM for evaluation and explanation
    evaluation_agent = start_llm(MODEL, ROLES.EVALUATOR)
    explanation_agent = start_llm(MODEL, ROLES.EXPLAINER)

    records = []
    try:
        pbar = tqdm(range(n_samples))
        for i in pbar:
            # Fetch the article inputs from the dataframe
            article_id = df_sample["id"].iloc[i]
            article_content = df_sample["extracted_content_body"].iloc[i]
            article_title = df_sample["title"].iloc[i]
            meta_desc = df_sample["category_description"].iloc[
                i
            ]  # meta_desc can be null
            meta_desc = meta_desc if meta_desc is not None else "No meta description"
            article_url = df_sample["full_url"].iloc[i]
            content_category = df_sample["content_category"].iloc[i]
            article_category_names = df_sample["article_category_names"].iloc[i]
            page_views = df_sample["page_views"].iloc[i]

            print(f"Checking {article_title} now...")
            # Set up Inputs for the Optimisation Checks graph
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
                "skip_llm_evaluations": {
                    "decision": False,
                    "explanation": None,
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
            try:
                # Execute the Optimisation Checks on the article
                response = execute_graph(app, inputs)
                print(response)
            except ValueError as value_error:
                # Skip LLM evaluations if Azure Content Filter is triggered
                message = (
                    getattr(value_error, "message", repr(value_error)).strip().lower()
                )
                if "content filter being triggered" in message:
                    print(
                        "Content Filter has been triggered.",
                        f"Article ID: {article_id}",
                        f"Article Title: {article_title}",
                        sep="\n",
                    )
                    print("Skipping LLM-based evaluations...", end="\n\n")
                    skip_llm_evaluations = {
                        "decision": True,
                        "explanation": "LLM unable to process content due to Azure's content filtering on hate, sexual, violence, and self-harm related categories",
                    }
                    inputs["skip_llm_evaluations"] = skip_llm_evaluations
                    response = execute_graph(app, inputs)
                    print(response)
                else:
                    raise value_error

            # Save output with the correct keys (Easier to parse into a Pandas DataFrame)
            result = format_checks_outputs(response)
            print("Result generated!")
            # Append the evaluations into records
            records.append(result)

            # Put the thread to sleep in order to avoid hitting the rate limit/token limit (Limits typically reset every minute)
            # Refer to the deployment configuration set on Azure or https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits#gpt-4o-rate-limits
            print("Sleeping for 15 seconds...")
            time.sleep(15)
            print("Awake!")

    # Handle Keyboard Interrupts in case the generation is caught in a deadlock (i.e. stalling)
    except KeyboardInterrupt:
        print("Interrupted!")

    # Handle Exceptions that may arise during the execution of the Optimisation Checks graph on the articles
    except Exception as ex:
        ex_type, ex_value, ex_traceback = sys.exc_info()
        print(f"Exception raised: {repr(ex)}")
        print(f"Exception type: {ex_type}")
        print(f"Exception value: {ex_value}")
        print("Exception traceback:")
        traceback.print_tb(ex_traceback)

    # Save the evaluated outputs into a new dataframe - Very useful esp when Keyboard Interrupts are executed. Generated evaluations are preserved.
    finally:
        print("Saving results...")
        save_evaluation_dataframe(records, df_evaluated)
        print("Completed.")
