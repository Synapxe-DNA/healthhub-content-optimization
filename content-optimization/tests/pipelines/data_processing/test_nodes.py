import re

import pandas as pd
import pytest
from kedro.io import DataCatalog
from src.content_optimization.pipelines.data_processing.nodes import (
    add_contents,
    extract_data,
    merge_data,
    standardize_columns,
)

pd.options.mode.chained_assignment = None


def test_standardize_columns(catalog: DataCatalog, num_cols: int = 28):
    """
    A test function for `standardize_columns` that checks the output data.

    Args:
        catalog (DataCatalog): The Kedro DataCatalog containing the necessary test datasets.
        num_cols (int): The expected number of columns in the standardized dataframe.

    Raises:
        AssertionError: If the output data does not meet the specified criteria (see below).

    Note:
        1. Expects a dictionary as output
        2. Expects the same number of content categories as input data
        3. Expects the correct number of columns in output data
        4. Expects a set of defined columns in output data
    """
    all_contents_standardized = standardize_columns(
        catalog.load("all_contents"),
        catalog.load("params:columns_to_add"),
        catalog.load("params:columns_to_keep"),
        catalog.load("params:default_columns"),
    )

    # Check if output is a dictionary
    assert isinstance(all_contents_standardized, dict), "Expected a dictionary"
    # Check if output contains only the correct number of content categories
    assert len(all_contents_standardized) == len(
        catalog.load("all_contents")
    ), "Number of content categories should match the input data"

    for _, df in all_contents_standardized.items():
        # Check if output contains the correct number of columns
        assert (
            df.shape[1] == num_cols
        ), f"Expected {num_cols} columns in the standardized dataframe but got {df.shape[1]}"
        # Check if output contains the expected columns
        assert (
            df.columns
            == [
                *catalog.load("params:default_columns"),
                # Added columns
                "content_category",
                "to_remove",
                "remove_type",
            ]
        ).all(), "Unexpected columns in the standardized dataframe"


def test_add_contents(catalog: DataCatalog):
    all_contents_standardized = catalog.load("all_contents_standardized")
    missing_contents = catalog.load("missing_contents")

    all_contents_added = add_contents(all_contents_standardized, missing_contents)

    # Check if output is a dictionary
    assert isinstance(all_contents_added, dict), "Expected a dictionary"

    # Check if output contains only the correct number of content categories
    assert len(all_contents_added) == len(
        catalog.load("all_contents")
    ), "Number of content categories should match the input data"

    friendly_urls = []

    # Store friendly_url in friendly_urls
    for file_path, _ in missing_contents.items():
        print(file_path)
        # Extract friendly url that is used as filename
        friendly_url = file_path.split("/")[-1]
        friendly_urls.append(friendly_url)

    # Combine all dataframes into one
    combined_df = pd.DataFrame()
    for content_category, partition_load_func in all_contents_added.items():
        df = partition_load_func()
        combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

    # Get articles with Excel Errors
    filtered_df = combined_df[combined_df["friendly_url"].isin(friendly_urls)]

    for index, row in filtered_df.iterrows():
        assert not re.match(
            r"Value exceeded maximum cell size", row["content_body"]
        ), "Content body was not successfully replaced"


@pytest.mark.parametrize("word_count_cutoff", [50, 90])
def test_extract_data(catalog: DataCatalog, word_count_cutoff: int):
    """
    A test function for `extract_data` that checks the output data.

    Args:
        catalog (DataCatalog): The Kedro DataCatalog containing the necessary test datasets.
        word_count_cutoff (int): The word count cutoff for the extracted content body.

    Raises:
        AssertionError: If the output data does not meet the specified criteria (see below).

    Note:
        1. Expects both outputs to be dictionaries
        2. Expects a set of defined columns in output data
        3. Expects the same number of articles with extracted content body as the number of output text files
        4. Expects the extracted content body to meet the word count cutoff
    """
    all_contents_extracted, all_extracted_text = extract_data(
        catalog.load("all_contents_extracted"),
        word_count_cutoff,
        catalog.load("params:whitelist"),
    )

    # Check if output is a dictionary
    assert isinstance(all_contents_extracted, dict), "Expected a dictionary"
    assert isinstance(all_extracted_text, dict), "Expected a dictionary"

    for content_category, df in all_contents_extracted.items():
        # Check if output contains the expected columns
        assert {
            "has_table",
            "has_image",
            "related_sections",
            "extracted_tables",
            "extracted_links",
            "extracted_headers",
            "extracted_img_alt_text",
            "extracted_content_body",
        }.issubset(df.columns), "Expected columns missing in the extracted dataframe"

        # Filter out articles that will be removed
        df_keep = df[~df["to_remove"]]

        # Check if number of articles with extracted content body matches the number of text files
        assert df_keep.shape[0] == len(
            [
                key
                for key in all_extracted_text.keys()
                if key.startswith(content_category)
            ]
        ), "Unexpected number of articles with extracted content body does not match the number of text files"

        # Check if extracted content body of removed articles are below the word count
        assert (
            df.query("remove_type == 'Below Word Count'")["extracted_content_body"]
            .apply(lambda x: len(x.split()) <= word_count_cutoff)
            .all()
        ), "Found extracted content body under `remove_type == Below Word Count`` above the word count cutoff"

        # Check if extracted content body of kept articles meets the word count cutoff
        assert (
            df_keep["extracted_content_body"]
            .apply(lambda x: len(x.split()) >= word_count_cutoff)
            .all()
        ), "Found extracted content body below the word count cutoff that is not removed"


def test_merge_data(catalog: DataCatalog):
    """
    A test function for `merge_data` that checks the output data.

    Args:
        catalog (DataCatalog): The Kedro DataCatalog containing the necessary test datasets.

    Raises:
        AssertionError: If the output data does not meet the specified criteria (see below).

    Note:
        1. Expects a dataframe as output
        2. Expects the total number of rows in the output data equal to the sum of the rows in the input data
    """
    all_contents_extracted = catalog.load("all_contents_extracted")
    merged_df = merge_data(all_contents_extracted)

    # Check if output is a dataframe
    assert isinstance(merged_df, pd.DataFrame), "Expected a dataframe"
    # Check if output contains the correct number of rows
    assert merged_df.shape[0] == sum(
        [
            partition_load_func().shape[0]
            for partition_load_func in all_contents_extracted.values()
        ]
    ), "Unexpected number of rows in the merged dataframe"


@pytest.mark.parametrize(
    "selected_content_category, missing_num_cols, num_cols",
    [
        ("cost-and-financing", 1, 24),
        ("live-healthy-articles", 3, 22),
        ("diseases-and-conditions", 5, 20),
        ("medications", 8, 17),
    ],
)
def test_standardize_columns_with_missing_column(
    catalog: DataCatalog,
    selected_content_category: str,
    missing_num_cols: int,
    num_cols: int,
):
    """
    Test the behavior of the `standardize_columns` function when a single or multiple columns are missing.

    This function tests the behavior of the `standardize_columns` function when a column is missing.
    It uses the `pytest.mark.parametrize` decorator to generate multiple test cases with different
    values for `selected_content_category`, `missing_num_cols`, and `num_cols`.

    Args:
        catalog (DataCatalog): The Kedro DataCatalog containing the necessary test datasets.
        selected_content_category (str): The selected content category.
        missing_num_cols (int): The number of missing columns.
        num_cols (int): The expected number of columns.

    Raises:
        ValueError: Raised if there is a length mismatch between the expected number of columns.
    """
    modified_columns_to_keep = {}

    for content_category, columns_to_keep in catalog.load(
        "params:columns_to_keep"
    ).items():
        if content_category == selected_content_category:
            modified_columns_to_keep[content_category] = columns_to_keep[
                :-missing_num_cols
            ]
        else:
            modified_columns_to_keep[content_category] = columns_to_keep

    with pytest.raises(ValueError) as error:
        _ = standardize_columns(
            catalog.load("all_contents"),
            catalog.load("params:columns_to_add"),
            modified_columns_to_keep,
            catalog.load("params:default_columns"),
        )

    # Check if the error message is as expected
    assert f"Length mismatch: Expected axis has {num_cols} elements" in str(error.value)
