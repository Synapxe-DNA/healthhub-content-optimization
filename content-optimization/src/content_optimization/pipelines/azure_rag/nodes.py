"""
This is a boilerplate pipeline 'azure_rag'
generated using Kedro 0.19.6
"""

from typing import Any, Dict, List

import pandas as pd
from content_optimization.pipelines.azure_rag.llm_extraction import ask


def filter_articles(
    merged_data: pd.DataFrame,
    azure_blacklist: List[int],
    azure_whitelist: List[int],
    lengthy_articles: List[int],
) -> pd.DataFrame:
    """
    Filters the input DataFrame by removing articles based on specific conditions.

    Args:
        merged_data (pd.DataFrame): DataFrame containing the merged article data.
        blacklist (List[int]): List of article IDs to be removed as duplicates.
        whitelist (List[int]): List of article IDs that contain duplicated content/url but should be kept.
        lengthy_articles (List[int]): List of article IDs for articles that are too lengthy and should be removed.

    Returns:
        pd.DataFrame: Filtered DataFrame after applying all conditions for removal.
    """
    # Apply the filtering conditions
    print(merged_data.head())
    # Apply the filtering conditions
    # Remove articles with 'No HTML Tags' from the 'remove_type' column
    filtered_data_rag = merged_data.loc[merged_data["remove_type"] != "No HTML Tags"]
    # Remove the rows with 'No Extracted Content' from 'remove_type' column
    filtered_data_rag = filtered_data_rag[
        filtered_data_rag["remove_type"] != "No Extracted Content"
    ]
    # Remove the rows with 'NaN' from 'remove_type' column
    filtered_data_rag = filtered_data_rag[filtered_data_rag["remove_type"] != "NaN"]
    # Remove 'Multilingual' from 'remove_type' column
    filtered_data_rag = filtered_data_rag[
        filtered_data_rag["remove_type"] != "Multilingual"
    ]

    # Remove 'URL Error' from 'remove_type' column
    filtered_data_rag = filtered_data_rag[
        filtered_data_rag["remove_type"] != "URL Error"
    ]

    # Remove the duplicated articles with specific 'id' values
    filtered_data_rag = filtered_data_rag[
        ~filtered_data_rag["id"].isin(azure_blacklist)
    ]

    # Remove 'Duplicated Content' from 'remove_type' column, except for specific 'id' values
    filtered_data_rag = filtered_data_rag[
        (filtered_data_rag["remove_type"] != "Duplicated Content")
        | (filtered_data_rag["id"].isin(azure_whitelist))
    ]

    # Remove the article that is too lengthy
    filtered_data_rag = filtered_data_rag[
        ~filtered_data_rag["id"].isin(lengthy_articles)
    ]

    return filtered_data_rag


def process_html_tables(
    filtered_data_rag: pd.DataFrame,
    temperature: int,
    max_tokens: int,
    n_completions: int,
    seed: int,
) -> pd.DataFrame:
    """
    Processes articles containing HTML tables by passing the content through an LLM for extraction.

    Args:
        filtered_data_rag (pd.DataFrame): Filtered DataFrame that may contain HTML table content.
        temperature (int): Sampling temperature to control the randomness in the LLM output.
        max_tokens (int): Maximum number of tokens to generate from the LLM.
        n_completions (int): Number of completion outputs to generate from the LLM.
        seed (int): Random seed for reproducibility.

    Returns:
        pd.DataFrame: DataFrame with an additional column containing processed table content.
    """
    processed_data_rag = filtered_data_rag.copy()

    def _process_row(row):
        if row["has_table"]:
            return ask(
                html_content=row["content_body"],
                temperature=temperature,
                max_tokens=max_tokens,
                n_completions=n_completions,
                seed=seed,
            )
        return None

    processed_data_rag["processed_table_content"] = processed_data_rag.apply(
        _process_row, axis=1
    )
    return processed_data_rag


def extract_content(
    processed_data_rag: pd.DataFrame,
    article_content_columns: List[str],
    table_content_columns: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts article content and table content into a structured dictionary format for further use.

    Args:
        processed_data_rag (pd.DataFrame): DataFrame containing the processed article and table content.
        article_content_columns (List[str]): List of column names for the article content.
        table_content_columns (List[str]): List of column names for the table content.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing extracted article and table content, with unique keys based on article IDs.
    """
    # Prepare the dictionary to hold data
    json_data_rag = {}

    # Loop through each row in the DataFrame using iterrows()
    for index, row in processed_data_rag.iterrows():
        row_id = row["id"]
        extracted_row_content = row[article_content_columns]
        has_table = extracted_row_content["has_table"]

        # Create the dictionary for the content
        extracted_data_content = extracted_row_content.drop("has_table").to_dict()
        extracted_data_content["content"] = str(
            extracted_data_content.pop("extracted_content_body")
        )
        extracted_data_content["id"] = str(row_id) + "_content"
        content_key = str(row_id) + "_content"

        # Append to the dictionary under the unique key
        if content_key not in json_data_rag:
            json_data_rag[content_key] = []
        json_data_rag[content_key].append(extracted_data_content)

        if has_table:
            # Create the dictionary for the table
            extracted_row_table = row[table_content_columns]
            extracted_data_table = extracted_row_table.to_dict()
            extracted_data_table["content"] = str(
                extracted_data_table.pop("processed_table_content")
            )
            extracted_data_table["id"] = str(row_id) + "_table"
            table_key = str(row_id) + "_table"

            # Append to the dictionary under the unique key
            if table_key not in json_data_rag:
                json_data_rag[table_key] = []
            json_data_rag[table_key].append(extracted_data_table)

    return json_data_rag
