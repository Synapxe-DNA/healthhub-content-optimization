"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

import os
import re
from typing import Any, Callable

import pandas as pd
from content_optimization.pipelines.data_processing.extractor import HTMLExtractor
from content_optimization.pipelines.data_processing.utils import (
    add_content_body,
    add_updated_urls,
    flag_articles_to_remove_after_extraction,
    flag_articles_to_remove_before_extraction,
    invert_ia_mappings,
    map_category_names,
    select_and_rename_columns,
)
from tqdm import tqdm


def standardize_columns(
    all_contents: dict[str, Callable[[], Any]],
    columns_to_add_cfg: dict[str, list[str]],
    columns_to_keep_cfg: dict[str, list[str]],
    default_columns: list[str],
) -> dict[str, pd.DataFrame]:
    """
    Standardizes the columns of multiple dataframes in a dictionary.

    This function takes in a dictionary of dataframes, where each dataframe is associated with a filename.
    It then standardizes the columns of each dataframe by performing the following steps:

    1. Get the content category from the filename.
    2. Load the dataframe using the provided partition function.
    3. Standardize the column names by selecting and renaming the columns.
    4. Mark articles with no content or with dummy content in the `to_remove` column.
    5. Add the standardized dataframe to the `all_contents_standardized` dictionary.

    The function returns a dictionary mapping content categories to the standardized dataframes.

    Args:
        all_contents (dict[str, Callable[[], Any]]):
            A dictionary containing the raw `partitions.PartitionedDataset`where the keys are the filenames and the
            values loads the raw excel data as `pandas.DataFrame`.

        columns_to_add_cfg (dict[str, list[str]]):
            A dictionary mapping content categories to lists of column names to add.

        columns_to_keep_cfg (dict[str, list[str]]):
            A dictionary mapping content categories to lists of column names to keep.

        default_columns (list[str]):
            A list of default column names to rename the columns of the dataframes to.

    Returns:
        dict[str, pd.DataFrame]:
            A dictionary that contains the standardized dataframes stored as partitioned parquet files, where the keys
            are the content categories and the values are the corresponding dataframes.
    """
    all_contents_standardized = {}

    pbar = tqdm(all_contents.items())

    for filename, partition_load_func in pbar:
        # Get content category from filename
        content_category = re.sub(r"export-published-", "", filename.split("_")[0])
        pbar.set_description(f"Standardizing: {content_category}")

        # Load partition data
        df = partition_load_func()

        # Standardize column names
        columns_to_add = columns_to_add_cfg.get(content_category, None)
        columns_to_keep = columns_to_keep_cfg.get(content_category, None)

        # Standardize columns
        df = select_and_rename_columns(
            df, columns_to_add, columns_to_keep, default_columns, content_category
        )

        # Strip all whitespaces across all strings in dataframe
        # See: https://github.com/Wilsven/healthhub-content-optimization/issues/53
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        all_contents_standardized[content_category] = df

    return all_contents_standardized


def add_data(
    all_contents_standardized: dict[str, Callable[[], Any]],
    missing_contents: dict[str, Callable[[], Any]],
    updated_urls: dict[str, dict[int, str]],
) -> dict[str, Callable[[], Any]]:
    """
    Process and add data to standardized content, incorporating missing contents and updated URLs.

    This function performs the following operations:
    1. Fetches missing content from text files to correct Excel errors.
    2. Adds content body to the dataframe for each content category.
    3. Updates URLs in the dataframe.
    4. Flags articles that should be removed before extraction.

    Args:
        all_contents_standardized (dict[str, Callable[[], Any]]): A dictionary where keys are content categories and
            values are functions that return dataframes of standardized content.
        missing_contents (dict[str, Callable[[], Any]]): A dictionary where keys are file paths and values are functions
            that load the content of text files.
        updated_urls (dict[str, dict[int, str]]): A dictionary where keys are content categories and values are
            dictionaries mapping the article IDs to updated URLs.

    Returns:
        dict[str, Callable[[], Any]]: A dictionary where keys are content categories and values are functions that return
            processed dataframes with added data.
    """
    excel_errors = {}
    all_contents_added = {}

    # Fetch all txt files from 01_raw to correct the Excel error
    for file_path, load_func in missing_contents.items():
        text = load_func()
        # Extract friendly url that is used as filename
        friendly_url = file_path.split("/")[-1]
        # Store in dictionary
        excel_errors[friendly_url] = text

    pbar = tqdm(all_contents_standardized.items())

    for content_category, partition_load_func in pbar:
        pbar.set_description(f"Adding: {content_category}")
        df = partition_load_func()

        # Add back contents that are previously indicated as excel errors into the `content_body` column
        df = add_content_body(df, excel_errors)

        # Add updated urls into the `full_url` column
        urls_dict = updated_urls.get(content_category, {})
        df = add_updated_urls(df, urls_dict)

        # Mark articles with no content, was rejected by Excel due to a "Value
        # exceeded maximum cell size" error or with dummy content in `to_remove` column
        df = flag_articles_to_remove_before_extraction(df)

        all_contents_added[content_category] = df

    return all_contents_added


def extract_data(
    all_contents_added: dict[str, Callable[[], Any]],
    word_count_cutoff: int,
    whitelist: list[int],
    blacklist: dict[int, str],
) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """
    Extracts data from processed content and stores it in parquet files
    and text files.

    Args:
        all_contents_added (dict[str, Callable[[], Any]]):
            A dictionary containing the standardized `partitions.PartitionedDataset` where the keys are the content
            categories and the values loads the updated parquet data as `pandas.DataFrame`.
        word_count_cutoff (int): The minimum number of words in an article to be considered before flagging for removal.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.
        blacklist (dict[int, str]): A dictionary containing the article IDs and the reason to remove it. See https://bitly.cx/f8FIk.

    Returns:
        tuple[dict[str, pd.DataFrame], dict[str, str]]: A tuple containing two dictionaries. The first dictionary
            contains the extracted data stored as partitioned parquet files, where the keys are the content categories
            and the values are the corresponding dataframes.
            The second dictionary contains the extracted text stored as partitioned text files, where the keys are the
            file paths and the values are the extracted text.
    """
    all_contents_extracted = {}  # to store as partitioned parquet files
    all_extracted_text = {}  # to store as partitioned text files

    pbar = tqdm(all_contents_added.items())

    for content_category, partition_load_func in pbar:
        pbar.set_description(f"Extracting: {content_category}")
        # Load partition data
        df = partition_load_func()

        # Initialise new columns in dataframe to store extracted data
        df["has_table"] = False
        df["has_image"] = False
        df["related_sections"] = None
        df["extracted_tables"] = None
        df["extracted_raw_html_tables"] = None
        df["extracted_links"] = None
        df["extracted_headers"] = None
        df["extracted_images"] = None
        df["extracted_content_body"] = None

        for index, row in df.iterrows():
            # Skip extraction for those articles flagged for removal unless whitelisted
            if row["to_remove"]:
                # Check if the article is in the whitelist
                if row["id"] not in whitelist:
                    continue
                else:
                    # Whitelist article
                    df.at[index, "to_remove"] = False

            # Replace all forward slashes with hyphens to avoid saving as folders
            title = re.sub(r"\/", "-", row["title"]).strip()

            # Get the HTML content for extraction and relevant data for logging
            content_name = row["content_name"]
            full_url = row["full_url"]
            html_content = row["content_body"]

            # Extract text from HTML using the HTMLExtractor Class
            extractor = HTMLExtractor(
                content_name, content_category, full_url, html_content
            )
            has_table = extractor.check_for_table()
            has_image = extractor.check_for_image()
            related_sections = extractor.extract_related_sections()
            extracted_tables = extractor.extract_tables()
            extracted_raw_html_tables = extractor.extract_raw_html_tables()
            extracted_links = extractor.extract_links()
            extracted_headers = extractor.extract_headers()
            extracted_img_alt_text = extractor.extract_img_links_and_alt_text()
            extracted_content_body = extractor.extract_text()

            # Store extracted data into the dataframe
            df.at[index, "has_table"] = has_table
            df.at[index, "has_image"] = has_image
            df.at[index, "related_sections"] = related_sections
            df.at[index, "extracted_tables"] = extracted_tables
            df.at[index, "extracted_raw_html_tables"] = extracted_raw_html_tables
            df.at[index, "extracted_links"] = extracted_links
            df.at[index, "extracted_headers"] = extracted_headers
            df.at[index, "extracted_images"] = extracted_img_alt_text
            df.at[index, "extracted_content_body"] = extracted_content_body

            # Substitute forbidden characters for filenames with _
            title = re.sub(r'[<>:"/\\|?*]', "_", title)

            # Truncate title to 25 characters and append the id
            # See: https://github.com/Wilsven/healthhub-content-optimization/issues/42
            title = title[:25] + f"_{row['id']}"

            # Store text files in its own folder named `content_category`
            all_extracted_text[os.path.join(content_category, title)] = (
                extracted_content_body
            )

        # After extraction, we flag to remove articles with no content,
        # duplicated content, duplicated URL or below word count cutoff
        df = flag_articles_to_remove_after_extraction(
            df, word_count_cutoff, whitelist, blacklist
        )

        # Store dataframes in a parquet file named `content_category`
        all_contents_extracted[content_category] = df

    return all_contents_extracted, all_extracted_text


def map_data(
    all_contents_extracted: dict[str, Callable[[], Any]],
    l1_mappings: dict[str, dict[str, list[str]]],
    l2_mappings: dict[str, dict[str, list[str]]],
) -> dict[str, Callable[[], Any]]:
    """
    Map extracted content data to L1 and L2 Information Architecture (IA) categories.

    This function applies the L1 and L2 IA mappings for each content category.
    It inverts the provided mappings, iterates through each content category, and applies the mappings to the
    'article_category_names' column in the dataframe.

    Args:
        all_contents_extracted (dict[str, Callable[[], Any]]): A dictionary where keys are content categories and values
            are functions that return dataframes of extracted content.
        l1_mappings (dict[str, dict[str, list[str]]]): A dictionary of L1 category mappings.
            The outer key is the content category, inner key is the target (new) category, and the value is a list of
            source (old) categories.
        l2_mappings (dict[str, dict[str, list[str]]]): A dictionary of L2 category mappings, structured similarly to
            l1_mappings.

    Returns:
        dict[str, Callable[[], Any]]: A dictionary where keys are content categories and values are functions that return
            dataframes with mapped L1 and L2 categories. The returned dataframes include new columns for the mapped categories.

    Note:
        - This function uses the `invert_ia_mappings` and `map_category_names` helper functions.
    """
    all_contents_mapped = {}
    inverted_l1_mappings = invert_ia_mappings(l1_mappings)
    inverted_l2_mappings = invert_ia_mappings(l2_mappings)

    pbar = tqdm(all_contents_extracted.items())

    for content_category, partition_load_func in pbar:
        pbar.set_description(f"Mapping: {content_category}")
        # Load partition data
        df = partition_load_func()

        # Map the values from the `article_category_names` column to the new L1 IA mapping
        mapped_l1_df = map_category_names(
            inverted_l1_mappings,
            df,
            "content_category",
            "article_category_names",
            "l1_mappings",
        )

        # Map the values from the `article_category_names` column to the new L2 IA mapping
        mapped_df = map_category_names(
            inverted_l2_mappings,
            mapped_l1_df,
            "content_category",
            "article_category_names",
            "l2_mappings",
        )

        all_contents_mapped[content_category] = mapped_df

    return all_contents_mapped


def merge_data(
    all_contents_mapped: dict[str, Callable[[], Any]],
    google_analytics_data: dict[str, pd.DataFrame],
    google_analytics_columns: dict[str, str],
) -> pd.DataFrame:
    """
    Merge the data from multiple partitioned dataframes into a single `pandas.DataFrame`.

    Parameters:
        all_contents_mapped (dict[str, Callable[[], Any]]):
            A dictionary containing the `partitions.PartitionedDataset` where the values load the parquet data as `pandas.DataFrame`.

        google_analytics_data: dict[str, pd.DataFrame]:
            A dictionary containing the `pandas.DataFrame` where the keys are the content categories and the values
            are the dataframes with the Google Analytics data.

        google_analytics_columns (dict[str, str]): A mapping to default column names for the Google Analytics data.

    Returns:
        pd.DataFrame: The merged dataframe with updated Google Analytics data.
    """
    merged_df = pd.DataFrame()
    for content_category, ga_df in google_analytics_data.items():
        # Rename columns and remove unnecessary columns
        df = ga_df.rename(columns=google_analytics_columns)
        df = df[["id", *google_analytics_columns.values()]]
        # Load partition data
        orig_df = all_contents_mapped[content_category]()
        # Drop outdated Google Analytics data columns
        orig_df = orig_df.drop(list(google_analytics_columns.values()), axis=1)
        # Merge data with updated Google Analytics statistics
        tmp = orig_df.merge(df, on="id")
        merged_df = pd.concat([merged_df, tmp], axis=0, ignore_index=True)

    return merged_df
