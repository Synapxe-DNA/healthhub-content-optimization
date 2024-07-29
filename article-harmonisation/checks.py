import os
from typing import Annotated, Any, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import END, START, MessagesState, StateGraph
from models import start_llm
from phoenix.trace.langchain import LangChainInstrumentor
from utils.evaluations import calculate_readability

# Setting the environment for HuggingFaceHub
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
os.environ["PHOENIX_PROJECT_NAME"] = os.getenv("PHOENIX_PROJECT_NAME", "")

# Available models configured to the project
MODELS = ["mistral", "llama3"]

# Declaring model to use
MODEL = MODELS[0]

# Declaring node roles
EVALUATOR = "Evaluator"
EXPLAINER = "Explainer"

# Declaring maximum new tokens
MAX_NEW_TOKENS = 3000


def merge_dict(dict1, dict2):
    for key, val in dict1.items():
        if isinstance(val, dict):
            if key in dict2 and type(dict2[key] == dict):
                merge_dict(dict1[key], dict2[key])
        else:
            if key in dict2:
                dict1[key] = dict2[key]

    for key, val in dict2.items():
        if key not in dict1:
            dict1[key] = val

    return dict1


class GraphState(TypedDict):
    """This class contains the different keys relevant to the project. It inherits from the TypedDict class.

    Attributes:
        article_content: A required String where each element is a String containing the article content.
        article_title: A required String which will contain the article title.
        meta_desc: A required String that will contain article's meta description.
        content_flags:
        title_flags:
        meta_flags:
        content_judge:
        title_judge:
        meta_judge:
        llm_agents:
    """

    # Article Inputs
    article_content: str
    article_title: str
    meta_desc: str

    # Flags for rule-based/statistical-based methods
    content_flags: Annotated[dict[str, bool], merge_dict]
    title_flags: Annotated[dict[str, bool], merge_dict]
    meta_flags: Annotated[dict[str, bool], merge_dict]

    # Explanations for various criteria
    content_judge: Annotated[dict[str, str], merge_dict]
    title_judge: Annotated[dict[str, str], merge_dict]
    meta_judge: Annotated[dict[str, str], merge_dict]

    # Agents
    llm_agents: dict[str, Any]


def content_evaluation_rules_node(state: MessagesState) -> str:
    article_content = state.get("article_content", "")
    content_flags = state.get("content_flags", {})

    # Check readability -
    # Hemmingway Metric
    metric = calculate_readability(article_content, "hemmingway")
    score = metric.get("score", -1)

    # NOTE: Exceptions must be handled to prevent the program from being prematurely terminated
    if score <= 0:
        raise ValueError("The readability score must be greater than 0.")
    elif score >= 10:
        content_flags["is_unreadable"] = True
    else:
        content_flags["is_unreadable"] = False

    # Check for insufficient content -
    # Less than 300 - 400 words is considered too brief
    # to adequately cover a topic unless it's a very specific and narrow subject
    # TODO: Plot the word count distribution of articles across each content category
    word_count = len(article_content.split())
    if word_count < 300:
        content_flags["low_word_count"] = True
    else:
        content_flags["low_word_count"] = False

    return {"content_flags": content_flags}


def content_evaluation_llm_node(state: MessagesState) -> str:
    article_content = state.get("article_content", "")
    content_judge = state.get("content_judge", {})
    content_evaluation_agent = state.get("llm_agents")["evaluation_agent"]

    # Check poor content structure -
    # No clear sections
    # No introduction or conclusion
    # Absence of headings or subheadings
    content_structure_eval = content_evaluation_agent.evaluate_content(
        article_content, choice="structure"
    )
    content_judge["structure"] = content_structure_eval

    # Check whether the writing guideline is followed given the tagged topic
    # Refer to Content Playbook - https://drive.google.com/file/d/1I6k4FDiX8zsARs4DAPnkhbtUl71K-bhv/view
    # TODO: Write up the functions and prompts that are category specific
    pass
    return {"content_judge": content_judge}


def content_explanation_node(state: MessagesState) -> str:
    article_content = state.get("article_content", "")
    content_flags = state.get("content_flags", {})
    content_judge = state.get("content_judge", {})

    # Explain Poor Readability based on Readability Matrix - Low Priority
    readabilty = content_flags.get("is_unreadable", False)

    if readabilty:
        explanation_agent = state.get("llm_agents")["explanation_agent"]
        readability_explanation = explanation_agent.evaluate_content(
            article_content, choice="readability"
        )
        content_judge["readability"] = readability_explanation

    return {"content_judge": content_judge}


def title_evaluation_rules_node(state: MessagesState) -> str:
    article_title = state.get("article_title", "")
    title_flags = state.get("title_flags", {})

    # Not Within Page Title Char Count - Up to 70 Characters
    # NOTE: Exceptions must be handled to prevent the program from being prematurely terminated
    # TODO: Check whether an error is raised for all articles - Stress test
    char_count = len(article_title)
    if char_count <= 0:
        raise ValueError("The title character count must be greater than 0.")
    elif char_count > 70:
        title_flags["long_title"] = True
    else:
        title_flags["long_title"] = False

    return {"title_flags": title_flags}


def title_evaluation_llm_node(state: MessagesState) -> str:
    article_title = state.get("article_title", "")
    article_content = state.get("article_content", "")
    title_judge = state.get("title_judge", {})

    # Irrelevant Page Title
    title_evaluation_agent = state.get("llm_agents")["evaluation_agent"]
    title_evaluation = title_evaluation_agent.evaluate_title(
        article_title, article_content
    )
    title_judge["title"] = title_evaluation

    return {"title_judge": title_judge}


def meta_desc_evaluation_rules_node(state: MessagesState) -> str:
    meta_desc = state.get("meta_desc", "")
    meta_flags = state.get("meta_flags", {})

    # Not Within Meta Description Char Count - Between 70 and 160 characters
    # NOTE: Exceptions must be handled to prevent the program from being prematurely terminated
    char_count = len(meta_desc)
    if char_count <= 0:
        raise ValueError("The meta description character count must be greater than 0.")
    elif 70 <= char_count <= 160:
        meta_flags["not_within_word_count"] = False
    else:
        meta_flags["not_within_word_count"] = True

    return {"meta_flags": meta_flags}


def meta_desc_evaluation_llm_node(state: MessagesState) -> str:
    meta_desc = state.get("meta_desc", "")
    article_content = state.get("article_content", "")
    meta_judge = state.get("meta_judge", {})

    # Irrelevant Meta Description
    meta_evaluation_agent = state.get("llm_agents")["evaluation_agent"]
    meta_evaluation = meta_evaluation_agent.evaluate_meta_description(
        meta_desc, article_content
    )
    meta_judge["meta_desc"] = meta_evaluation

    return {"meta_judge": meta_judge}


# Creating a StateGraph object with GraphState as input.
workflow = StateGraph(GraphState)

# Adding the nodes to the workflow
workflow.add_node("content_evaluation_rules_node", content_evaluation_rules_node)
workflow.add_node("content_explanation_node", content_explanation_node)
workflow.add_node("content_evaluation_llm_node", content_evaluation_llm_node)
workflow.add_node("title_evaluation_rules_node", title_evaluation_rules_node)
workflow.add_node("title_evaluation_llm_node", title_evaluation_llm_node)
workflow.add_node("meta_desc_evaluation_rules_node", meta_desc_evaluation_rules_node)
workflow.add_node("meta_desc_evaluation_llm_node", meta_desc_evaluation_llm_node)

# Content Evaluation
workflow.add_edge(START, "content_evaluation_rules_node")
workflow.add_edge("content_evaluation_rules_node", "content_explanation_node")
workflow.add_edge("content_explanation_node", "content_evaluation_llm_node")
workflow.add_edge("content_evaluation_llm_node", END)

# Title Evaluation
workflow.add_edge(START, "title_evaluation_rules_node")
workflow.add_edge("title_evaluation_rules_node", "title_evaluation_llm_node")
workflow.add_edge("title_evaluation_llm_node", END)

# Meta Description Evaluation
workflow.add_edge(START, "meta_desc_evaluation_rules_node")
workflow.add_edge("meta_desc_evaluation_rules_node", "meta_desc_evaluation_llm_node")
workflow.add_edge("meta_desc_evaluation_llm_node", END)


graph = workflow.compile()


if __name__ == "__main__":
    # Save Graph
    img = graph.get_graph(xray=True).draw_mermaid_png()
    with open("checks.png", "wb") as f:
        f.write(img)

    # Start LLM
    evaluation_agent = start_llm(MODEL, EVALUATOR)
    explanation_agent = start_llm(MODEL, EXPLAINER)

    LangChainInstrumentor().instrument()

    # Load data from merged_data.parquet and randomly sample 30 rows
    df = pd.read_parquet("./data/merged_data.parquet")
    df_keep = df[~df["to_remove"]]
    df_sample = df_keep.sample(n=30, replace=False, random_state=42)
    rows = df_sample.shape[0]
    print(rows)

    for i in range(rows):
        # Set up
        article_content = df_sample["extracted_content_body"].iloc[i]
        article_title = df_sample["title"].iloc[i]
        meta_desc = df_sample["category_description"].iloc[i]  # meta_desc can be null
        meta_desc = meta_desc if meta_desc is not None else "No meta description"

        print(f"Checking {article_title} now...")
        records = []
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

        response = graph.invoke(input=inputs)
        print(response)
        del response["llm_agents"]
        records.append(response)

    df_save = pd.DataFrame.from_records(records)
    df_save.to_parquet("./data/agentic_response.parquet")
