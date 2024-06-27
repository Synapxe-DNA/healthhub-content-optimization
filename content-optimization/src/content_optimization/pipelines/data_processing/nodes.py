"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

import os
import re
from typing import Any, Callable

import pandas as pd
from alive_progress import alive_bar
from content_optimization.pipelines.data_processing.preprocess import HTMLExtractor


def process_data(
    all_contents: dict[str, Callable[[], Any]],
    columns_to_keep: dict[str, list[str]],
    metadata: dict[str, dict[str, str]],
) -> dict[str, pd.DataFrame]:
    """
    Process the data by loading, filtering, and keeping selected columns
    specified in the configuration.

    Args:
        all_contents (dict[str, Callable[[], Any]]):
            A dictionary containing all the raw contents, where
            the keys are the filenames and the values are
            the partition functions to load the corresponding dataframes.

        columns_to_keep (dict[str, list[str]]):
            A dictionary mapping content categories to relevant columns to keep
            as specified in the configuration.

        metadata (dict[str, dict[str, str]]):
            A dictionary containing the metadata for each content category,
            where the keys are the content categories and the values are
            dictionaries with the keys "content_title" and "content_body"
            representing the column names for the article title and body of
            the HTML content, respectively.

    Returns:
        dict[str, pd.DataFrame]:
            A dictionary that contains the processed dataframe stored as partitioned
            parquet files, where the keys are the content categories and the values are
            the corresponding dataframes.
    """
    all_contents_processed = {}

    with alive_bar(len(all_contents), title="Processing data", force_tty=True) as bar:
        for filename, partition_load_func in all_contents.items():
            # Get content category from filename
            content_category = re.sub(r"export-published-", "", filename.split("_")[0])
            bar.text(f"Processing: {content_category}")

            # Load the dataframe
            df = partition_load_func()

            # Drop all columns which have only null values
            df = df.dropna(axis=1, how="all")

            relevant_columns = columns_to_keep[content_category]
            # Keep all relevant columns
            df = df[relevant_columns]

            content_body = metadata[content_category]["content_body"]

            # Mark articles with no content `to_remove`
            df["to_remove"] = df[content_body].apply(
                lambda x: (
                    False
                    if pd.notna(x) and re.search(r"(<[div|p|h2].*?>)", str(x))
                    else True
                )
            )

            all_contents_processed[content_category] = df
            bar()

    return all_contents_processed


def extract_data(
    all_contents_processed: dict[str, Callable[[], Any]],
    metadata: dict[str, dict[str, str]],
) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """
    Extracts data from processed content and stores it in parquet files
    and text files.

    Args:
        all_contents_processed (dict[str, Callable[[], Any]]):
            A dictionary containing the processed content, where
            the keys are the content categories and the values are
            the partition functions to load the corresponding dataframes.

        metadata (dict[str, dict[str, str]]):
            A dictionary containing the metadata for each content category,
            where the keys are the content categories and the values are
            dictionaries with the keys "content_title" and "content_body"
            representing the column names for the article title and body of
            the HTML content, respectively.

    Returns:
        tuple[dict[str, pd.DataFrame], dict[str, str]]:
            A tuple containing two dictionaries. The first dictionary contains
            the extracted data stored as partitioned parquet files, where the keys
            are the content categories and the values are the corresponding dataframes.
            The second dictionary contains the extracted text stored as partitioned
            text files, where the keys are the file paths and the values are the extracted
            text.
    """
    all_contents_extracted = {}  # to store as partitioned parquet files
    all_extracted_text = {}  # to store as partitioned text files

    with alive_bar(
        len(all_contents_processed), title="Extracting data", force_tty=True
    ) as bar:
        for content_category, partition_load_func in all_contents_processed.items():
            bar.text(f"Extracting: {content_category}")

            # Load the dataframe
            df = partition_load_func()

            uuid = metadata[content_category]["uuid"]
            content_title = metadata[content_category]["content_title"]
            content_body = metadata[content_category]["content_body"]

            # Initialise new columns in dataframe to store extracted data
            df["related_sections"] = None
            df["extracted_content_body"] = None
            df["extracted_links"] = None
            df["extracted_headers"] = None

            for index, row in df.iterrows():
                # Skip extraction for those articles flagged for removal
                if row["to_remove"]:
                    continue

                # Replace all forward slashes with hyphens to avoid saving as folders
                title = re.sub(r"\/", "-", row[content_title]).strip()

                # Get the HTML content
                html_content = row[content_body]

                # Extract text from HTML using the HTMLExtractor Class
                extractor = HTMLExtractor(html_content)
                related_sections = extractor.extract_related_sections()
                extracted_content_body = extractor.extract_text()
                extracted_links = extractor.extract_links()
                extracted_headers = extractor.extract_headers()

                # Store extracted data into the dataframe
                df.at[index, "related_sections"] = related_sections
                df.at[index, "extracted_content_body"] = extracted_content_body
                df.at[index, "extracted_links"] = extracted_links
                df.at[index, "extracted_headers"] = extracted_headers

                # If `extracted_content_body` is empty, we update flag to remove
                if extracted_content_body == "":
                    df.at[index, "to_remove"] = True

                # Substitute forbidden characters for filenames with _
                title = re.sub(r'[<>:"/\\|?*]', "_", title)

                # Truncate title to 25 characters and append the id
                # See: https://github.com/Wilsven/healthhub-content-optimization/issues/42
                title = title[:25] + f"_{row[uuid]}"

                # Store text files in its own folder named `content_category`
                all_extracted_text[os.path.join(content_category, title)] = (
                    extracted_content_body
                )

            # Store dataframes in a parquet file named `content_category`
            all_contents_extracted[content_category] = df
            bar()

    return all_contents_extracted, all_extracted_text
