import pandas as pd
import pytest
from kedro.io import DataCatalog
from src.content_optimization.pipelines.data_processing.nodes import (
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
        catalog.load("all_contents_standardized"),
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
        }.issubset(df.columns), "Exptected columns missing in the extracted dataframe"

        # Check if number of articles with extracted content body matches the number of text files
        assert df.query("to_remove == False").shape[0] == len(
            [
                key
                for key in all_extracted_text.keys()
                if key.startswith(content_category)
            ]
        ), "Unexpected number of articles with extracted content body does not match the number of text files"
        # Check if extracted content body meets the word count cutoff
        assert (
            df.query("remove_type == 'Below Word Count'")["extracted_content_body"]
            .apply(lambda x: len(x.split()) <= word_count_cutoff)
            .all()
        ), "Found extracted content body above the word count cutoff"


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
