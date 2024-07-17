import re
import warnings

import numpy as np
import pandas as pd
from pandas.errors import SettingWithCopyWarning

warnings.filterwarnings("ignore", category=SettingWithCopyWarning)


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

    # Set `remove_type` for all indexes
    df.loc[na_indexes, "remove_type"] = "NaN"
    df.loc[excel_error_indexes, "remove_type"] = "Excel Error"
    df.loc[no_tags_indexes, "remove_type"] = "No HTML Tags"

    return df


def flag_no_extracted_content(df: pd.DataFrame, whitelist: list[int]) -> pd.DataFrame:
    """
    Flags rows in the given DataFrame where the `extracted_content_body` column is empty.

    Args:
        df (pd.DataFrame): The DataFrame to flag rows in.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.

    Returns:
        pd.DataFrame:
            The modified DataFrame with the `to_remove` and `remove_type` columns updated. The `remove_type`
            column is updated with the type of "No Extracted Content".
    """
    # All content ids without extracted content
    no_extracted_content_ids = set(
        df[df["extracted_content_body"] == ""].id.to_list()
    ).difference(set(whitelist))

    # All content without extracted content indexes
    no_extracted_content_indexes = df.query(
        f"id in {list(no_extracted_content_ids)}"
    ).index

    # Update `to_remove`
    df.loc[no_extracted_content_indexes, "to_remove"] = True

    # Set `remove_type` for all indexes
    df.loc[no_extracted_content_indexes, "remove_type"] = "No Extracted Content"

    return df


def flag_duplicated(
    df: pd.DataFrame, whitelist: list[int], column: str
) -> pd.DataFrame:
    """
    Flags duplicated rows in the given DataFrame based on the specified column.
    This function only inspects for duplicates in two columns:
    `extracted_content_body` and `full_url`.

    Args:
        df (pd.DataFrame): The DataFrame to flag duplicated rows in.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.
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
                # Ignore whitelisted articles
                if df.iloc[j]["id"] in whitelist:
                    continue
                # Update `to_remove`
                df.at[j, "to_remove"] = True

                # Set `remove_type` for all indexes (either "Duplicated Content" or "Duplicated URL")
                df.at[j, "remove_type"] = value

    return df


def flag_recipe_articles(df: pd.DataFrame, whitelist: list[int]) -> pd.DataFrame:
    """
    Process the DataFrame to flag recipe articles based on `title`, `keywords` and
    `extracted_content_body` column.

    Parameters:
        df (pd.DataFrame): The DataFrame to flag recipe articles in.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.

    Returns:
        pd.DataFrame:
            The modified DataFrame with the `to_remove` and `remove_type` columns updated. The `remove_type`
            column is updated with the type of "Recipe".
    """

    # `title` and `keywords` column
    recipe_title_keywords_indexes = np.argwhere(
        [
            (
                True
                if (
                    (title is not None and re.search(r"[rR]ecipes?", title))
                    or (keywords is not None and re.search(r"[rR]ecipes?", keywords))
                )
                and (not to_remove)
                else False
            )
            for title, keywords, to_remove in zip(
                df["title"], df["keywords"], df["to_remove"]
            )
        ]
    ).flatten()

    # `extracted_content_body` column
    recipe_content_indexes = np.argwhere(
        [
            (
                True
                if (
                    content is not None
                    and re.search(r"what [do ]?you need", content.lower())
                    and re.search(r"how to cook [this dish]*", content.lower())
                )
                and (not to_remove)
                else False
            )
            for content, to_remove in zip(df["extracted_content_body"], df["to_remove"])
        ]
    ).flatten()

    # All recipe article indexes
    all_recipe_indexes = list(
        set(recipe_title_keywords_indexes).union(set(recipe_content_indexes))
    )

    # All content ids that are flagged as recipes
    recipe_ids = set(df.iloc[all_recipe_indexes].id.to_list()).difference(
        set(whitelist)
    )

    # All content below word count cutoff indexes
    recipe_indexes = df.query(f"id in {list(recipe_ids)}").index

    # Update `to_remove`
    df.loc[recipe_indexes, "to_remove"] = True

    # Set `remove_type` for all indexes
    df.loc[recipe_indexes, "remove_type"] = "Recipe"

    return df


def flag_below_word_count_cutoff(
    df: pd.DataFrame, word_count_cutoff: int, whitelist: list[int]
) -> pd.DataFrame:
    """
    Flags articles in a DataFrame based on the word count in the extracted content body.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        word_count_cutoff (int):
            The word count for an article to be flagged. If the word count falls below this
            threshold, the article is flagged.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.

    Returns:
        pd.DataFrame:
            The DataFrame with a new column `to_remove` indicating whether an article should be
            removed. The `remove_type` column is also updated with the type of "Below Word Count".

    """
    indexes = df.query("to_remove != True")["extracted_content_body"].apply(
        lambda x: len(x.split()) > 0 and len(x.split()) <= word_count_cutoff
    )

    # Get the indexes of the True values
    all_word_count_indexes = indexes[indexes].index

    # All content ids below word count cutoff
    word_count_ids = set(df.iloc[all_word_count_indexes].id.to_list()).difference(
        set(whitelist)
    )

    # All content below word count cutoff indexes
    word_count_indexes = df.query(f"id in {list(word_count_ids)}").index

    # Update `to_remove`
    df.loc[word_count_indexes, "to_remove"] = True

    # Set `remove_type` for all indexes
    df.loc[word_count_indexes, "remove_type"] = "Below Word Count"

    return df


def flag_multilingual_content(df: pd.DataFrame, whitelist: list[int]) -> pd.DataFrame:
    """
    Flags articles in a DataFrame if it is purely Chinese, Malay or Tamil.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.

    Returns:
        pd.DataFrame:
            The DataFrame with a new column `to_remove` indicating whether an article should be
            removed. The `remove_type` column is also updated with the type of "Multilingual".
    """

    def find_multilingual(friendly_url: str) -> bool:
        """
        Find multilingual articles as True
        Args:
            friendly_url: The file pointer of the article relative to the URL

        Returns:
            bool: True if the article is multilingual, False otherwise

        """
        # Return false if value is None
        if friendly_url is None:
            return False

        # Get the last word from the friendly_url
        check_lang = friendly_url.split("_")[-1]
        check_lang = check_lang.split("-")[-1]
        if re.search("(chinese|tamil|malay)", check_lang):
            return True
        else:
            return False

    # Find articles that are purely Chinese, Malay or Tamil
    all_multilingual_indexes = df.index[
        df["friendly_url"].apply(find_multilingual)
    ].to_list()
    # Find articles that are already considered as `to_remove`
    removed_indexes = df.index[df["to_remove"]].to_list()
    # Filter out removed_indexes from all_multilingual_indexes
    filtered_multilingual_indexes = list(
        set(all_multilingual_indexes).difference(set(removed_indexes))
    )
    # Filter out multilingual articles that are not whitelisted
    multilingual_ids = set(
        df.iloc[filtered_multilingual_indexes].id.to_list()
    ).difference(set(whitelist))

    # All content below word count cutoff indexes
    multilingual_indexes = df.query(f"id in {list(multilingual_ids)}").index

    # Update `to_remove`
    df.loc[multilingual_indexes, "to_remove"] = True
    # Set remove_type for all indexes
    df.loc[multilingual_indexes, "remove_type"] = "Multilingual"

    return df


def flag_articles_to_remove_after_extraction(
    df: pd.DataFrame, word_count_cutoff: int, whitelist: list[int]
) -> pd.DataFrame:
    """
    Flags articles to remove after extraction based on several different criteria.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        word_count_cutoff (int): The word count threshold for flagging articles.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.

    Returns:
        pd.DataFrame: The DataFrame with updated flags for articles to remove.
    """
    df = flag_no_extracted_content(df, whitelist)
    df = flag_duplicated(df, whitelist, column="extracted_content_body")
    df = flag_duplicated(df, whitelist, column="full_url")
    df = flag_recipe_articles(df, whitelist)
    df = flag_multilingual_content(df, whitelist)
    df = flag_below_word_count_cutoff(df, word_count_cutoff, whitelist)

    return df
