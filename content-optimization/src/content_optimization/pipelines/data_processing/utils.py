import re

import pandas as pd


def select_and_rename_columns(
    df: pd.DataFrame,
    columns_to_add: list[str] | None,
    columns_to_keep: list[str],
    default_columns: list[str],
    content_category: str,
) -> pd.DataFrame:
    """
     Select, rearrange, and rename columns in a DataFrame, and add a content category.

     This function performs the following operations:
     1. Drops columns with only null values.
     2. Optionally adds back specified columns.
     3. Rearranges columns based on a specified order.
     4. Renames columns to default names.
     5. Adds a content category column.

    Args:
         df: pd.DataFrame
             The input DataFrame to be processed.
         columns_to_add: list[str] | None
             List of column names to add back if they were dropped due to being all null.
             If None, no columns are added back.
         columns_to_keep: list[str]
             List of column names to keep, in the desired order.
         default_columns: list[str]
             List of new column names to replace the existing ones.
         content_category: str
             The content category to be added as a new column.

     Returns:
         pd.DataFrame:
             A new DataFrame with selected and renamed columns, and an added content category.

     Notes:
         - The function assumes that the length of `columns_to_keep` and `default_columns` are the same.
         - Columns not in `columns_to_keep` will be dropped from the resulting DataFrame.
    """
    # Drop all columns which have only null values
    df = df.dropna(axis=1, how="all")

    if columns_to_add is not None:
        # Add back selected columns which were dropped because they contained only null values
        df = df.reindex(columns=[*df.columns, *columns_to_add])

    # Rearrange columns to they are in order of `columns_to_keep`
    df = df[columns_to_keep]

    # Rename columns to default columns
    df.columns = default_columns

    # Tag the dataframe with the content category
    df["content_category"] = content_category

    return df


def flag_articles_to_remove_before_extraction(
    df: pd.DataFrame, regex: str = r"(<[div|p|h2].*?>)"
) -> pd.DataFrame:
    """
    Flags articles to remove before extraction based on a given regex pattern or
    because it contains no content or has was rejected by Excel due to a "Value
    exceeded maximum cell size" error. The default regex pattern flags out dummy
    content. Dummy content are content without the necessary HTML tags.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        regex (str):
            The regex pattern to search for in the `content_body` column.
            Defaults to r"(<[div|p|h2].*?>)".

    Returns:
        pd.DataFrame: The DataFrame with a new column `to_remove` indicating whether an article should be removed.
    """
    excel_error = "Value exceeded maximum cell size"

    def apply_regex(x: str) -> bool:
        # Define the regex pattern
        pattern = re.compile(regex)

        if pd.isna(x) or excel_error in str(x):
            return True
        return bool(pattern.search(str(x)))

    # Update `to_remove`
    df["to_remove"] = df["content_body"].apply(
        lambda x: (False if pd.notna(x) and re.search(regex, str(x)) else True)
    )

    # Get indexes for all NaN content body
    na_indexes = df[df["content_body"].isna()].index
    # Get all indexes for content body with Excel error
    excel_error_indexes = df.query(
        f"content_body.str.contains('{excel_error}', na=False)"
    ).index
    # Get all indexes content body without HTML tags indexes
    no_tags_indexes = df[
        ~df.query("content_category.notna()")["content_body"].apply(
            lambda x: apply_regex(x)
        )
    ].index

    df["remove_type"] = None

    # Set remove_type for all indexes
    df.loc[na_indexes, "remove_type"] = "NaN"
    df.loc[excel_error_indexes, "remove_type"] = "Excel Error"
    df.loc[no_tags_indexes, "remove_type"] = "No HTML Tags"

    return df


def flag_no_extracted_content(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flags rows in the given DataFrame where the `extracted_content_body` column is empty.

    Args:
        df (pd.DataFrame): The DataFrame to flag rows in.

    Returns:
        pd.DataFrame:
            The modified DataFrame with the `to_remove` and `remove_type` columns updated. The `remove_type`
            column is updated with the type of "No Extracted Content".
    """
    no_extracted_content_indexes = df.query("extracted_content_body == ''").index

    # Update `to_remove`
    df.loc[no_extracted_content_indexes, "to_remove"] = True

    # Set remove_type for all indexes
    df.loc[no_extracted_content_indexes, "remove_type"] = "No Extracted Content"

    return df


def flag_duplicated(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Flags duplicated rows in the given DataFrame based on the specified column.
    This function only inspects for duplicates in two columns:
    `extracted_content_body` and `full_url`.

    Args:
        df (pd.DataFrame): The DataFrame to flag duplicated rows in.
        column (str):
            The column to check for duplicated values. Must be either
            `extracted_content_body` and `full_url`.

    Returns:
        pd.DataFrame:
            The DataFrame with a new column `to_remove` indicating whether a row
            should be removed. The `remove_type` column is also updated with the type of
            "Duplicated Content" or "Duplicated URL".

    Raises:
        AssertionError: If the `column` parameter is None or not valid.
    """
    assert column is not None, "`column` cannot be None"
    assert column in ["extracted_content_body", "full_url"], "Invalid column"

    if column == "extracted_content_body":
        duplicated_df = df[
            (df[column].duplicated())  # we want duplicated articles
            & (df[column].notna())  # ignore null values
            & (df[column] != "")  # ignore empty extracted content
            & (~df["to_remove"])  # ignore articles that were already flagged
        ]
        value = "Duplicated Content"

    elif column == "full_url":
        duplicated_df = df[
            (df[column].duplicated())  # we want duplicated URLs
            & (df[column].notna())  # ignore null values
            & (~df["to_remove"])  # ignore articles that were already flagged
        ]
        value = "Duplicated URL"

    for i in range(len(duplicated_df)):
        # Get all indexes for duplicated content or URL
        duplicated_indexes = df[df[column] == duplicated_df.iloc[i][column]].index

        # Note: We could simply update all at once at `duplicated_indexes`
        # However, we'd overwrite the previous flags. This is kept as is, for now.
        for j in duplicated_indexes:
            if not df.iloc[j]["to_remove"]:
                # Update `to_remove`
                df.at[j, "to_remove"] = True

                # Set remove_type for all indexes (either "Duplicated Content" or "Duplicated URL")
                df.at[j, "remove_type"] = value

    return df


def flag_below_word_count_cutoff(
    df: pd.DataFrame, word_count_cutoff: int
) -> pd.DataFrame:
    """
    Flags articles in a DataFrame based on the word count in the extracted content body.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        word_count_cutoff (int):
            The word count for an article to be flagged. If the word count falls below this
            threshold, the article is flagged.

    Returns:
        pd.DataFrame:
            The DataFrame with a new column `to_remove` indicating whether an article should be
            removed. The `remove_type` column is also updated with the type of "Below Word Count".

    """
    indexes = df.query(
        "extracted_content_body.notna() "
        "and remove_type != 'Duplicated Content' "
        "and remove_type != 'Duplicated URL'"
    )["extracted_content_body"].apply(
        lambda x: len(x.split()) > 0 and len(x.split()) <= word_count_cutoff
    )

    # Get the indices of the True values
    word_count_indexes = indexes[indexes].index

    # Update `to_remove`
    df.loc[word_count_indexes, "to_remove"] = True

    # Set remove_type for all indexes
    df.loc[word_count_indexes, "remove_type"] = "Below Word Count"

    return df


def flag_articles_to_remove_after_extraction(
    df: pd.DataFrame, word_count_cutoff: int
) -> pd.DataFrame:
    """
    Flags articles to remove after extraction based on several different criteria.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        word_count_cutoff (int): The word count threshold for flagging articles.

    Returns:
        pd.DataFrame: The DataFrame with updated flags for articles to remove.
    """
    df = flag_no_extracted_content(df)
    df = flag_duplicated(df, column="extracted_content_body")
    df = flag_duplicated(df, column="full_url")
    df = flag_below_word_count_cutoff(df, word_count_cutoff)

    return df
