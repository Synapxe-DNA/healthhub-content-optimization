"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

import os
import re
from typing import Any, Callable

import pandas as pd
from alive_progress import alive_bar
from content_optimization.pipelines.data_processing.preprocess import extract_content


def preprocess_data(
    all_contents: dict[str, Callable[[], Any]],
    content_category: str,
    columns_to_drop: dict[str, list[str]],
    metadata: dict[str, dict[str, str]],
) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """
    Preprocesses the data for a given content category.

    Args:
        all_contents (dict[str, Callable[[], Any]]): A dictionary mapping
            content keys to functions that load the corresponding dataframes.
        content_category (str): The category of the content to preprocess.
        columns_to_drop (dict[str, list[str]]): A dictionary mapping content
            categories to lists of columns to drop.
        metadata (dict[str, dict[str, str]]): A dictionary mapping content
            categories to dictionaries containing metadata for the content.

    Returns:
        tuple[dict[str, pd.DataFrame], dict[str, str]]: A tuple containing two
            dictionaries. The first dictionary maps content categories to preprocessed
            dataframes, and the second dictionary maps titles to extracted content bodies.
    """
    print(content_category)  # for debugging

    all_contents_extracted = {}  # to store as partitioned excel files
    all_extracted_text = {}  # to store as partitioned text files

    # Get the key to access the `partition_load_func` which loads the dataframe
    key = f"export-published-{content_category}_14062024_data.xlsx"
    partition_load_func = all_contents[key]
    # Load the dataframe
    df = partition_load_func()

    # Drop all columns which have only null values
    df = df.dropna(axis=1, how="all")

    irrelevant_columns = columns_to_drop[content_category]
    # Drop all irrelevant columns
    df = df.drop(irrelevant_columns, axis=1)

    content_title = metadata[content_category]["content_title"]
    content_body = metadata[content_category]["content_body"]

    # Drop all articles with no content
    df = df[
        df[content_body].apply(
            lambda x: True if re.search(r"(<[div|p|h2].*?>)", x) else False
        )
    ].reset_index(drop=True)

    # Add new columns to store extracted data
    df["related_sections"] = None
    df["extracted_content_body"] = None

    with alive_bar(len(df), title="Extracting content body", force_tty=True) as bar:
        for index, row in df.iterrows():
            # Replace all forward slashes with hyphens to avoid saving as folders
            title = re.sub(r"\/", "-", row[content_title]).strip()

            # Get the HTML content
            html_content = row[content_body]
            # Extract text from HTML
            related_sections, extracted_content_body = extract_content(html_content)

            # Store extracted data into the dataframe
            df.at[index, "related_sections"] = related_sections
            df.at[index, "extracted_content_body"] = extracted_content_body

            # Store text files in its own folder named `content_category`
            all_extracted_text[os.path.join(content_category, title)] = (
                extracted_content_body
            )
            bar()

    # Store dataframes in a parquet named `content_category`
    all_contents_extracted[content_category] = df

    return all_contents_extracted, all_extracted_text
