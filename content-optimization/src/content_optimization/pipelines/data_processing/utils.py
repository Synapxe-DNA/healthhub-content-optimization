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
            (
                df[column].duplicated(keep="first")
            )  # we want duplicated articles, first instance is not flagged
            & (df[column].notna())  # ignore null values
            & (df[column] != "")  # ignore empty extracted content
            & (~df["to_remove"])  # ignore articles that were already flagged
        ]

        value = "Duplicated Content"

    elif column == "full_url":
        duplicated_df = df[
            (
                df[column].duplicated(keep="first")
            )  # we want duplicated URLs, first instance is not flagged
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

    def find_multilingual(friendly_url: str | None = None) -> bool:
        """
        A function that checks if a friendly URL is purely Chinese, Malay, or Tamil.

        Args:
            friendly_url (str | None): The friendly URL to check.

        Returns:
            bool: True if the friendly URL is purely Chinese, Malay, or Tamil, False otherwise.
        """
        # Return false if value is None
        if friendly_url is None:
            return False

        # Get the last word from the friendly_url
        check_lang = friendly_url.split("_")[-1].split("-")[-1]
        return True if re.search("(chinese|tamil|malay)", check_lang.lower()) else False

    # Find articles that are purely Chinese, Malay or Tamil
    all_multilingual_indexes = df.index[
        df["friendly_url"].apply(find_multilingual)
    ].to_list()

    # Find articles that are already considered as `to_remove`
    removed_indexes = df.index[df["to_remove"]].to_list()

    # Filter out `removed_indexes` from all_multilingual_indexes
    filtered_multilingual_indexes = list(
        set(all_multilingual_indexes).difference(set(removed_indexes))
    )
    # Filter out multilingual articles that are not whitelisted
    multilingual_ids = set(
        df.iloc[filtered_multilingual_indexes].id.to_list()
    ).difference(set(whitelist))

    # All content mulitlingual indexes
    multilingual_indexes = df.query(f"id in {list(multilingual_ids)}").index

    # Update `to_remove`
    df.loc[multilingual_indexes, "to_remove"] = True

    # Set `remove_type` for all indexes
    df.loc[multilingual_indexes, "remove_type"] = "Multilingual"

    return df


def flag_articles_via_blacklist(
    df: pd.DataFrame, blacklist: dict[int, str]
) -> pd.DataFrame:
    """
    Flags articles to remove based on blacklist provided in `parameters_data_processing.yml`

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        blacklist (dict[int, str]): The list of article IDs to remove. See https://bitly.cx/f8FIk.

    Returns:
        pd.DataFrame: The DataFrame with updated flags for articles to remove.
    """
    for article_id, remove_type in blacklist.items():
        idx = df.loc[df["id"] == article_id].index
        df.loc[idx, "to_remove"] = True
        df.loc[idx, "remove_type"] = remove_type

    return df


def flag_articles_to_remove_after_extraction(
    df: pd.DataFrame,
    word_count_cutoff: int,
    whitelist: list[int],
    blacklist: dict[int, str],
) -> pd.DataFrame:
    """
    Flags articles to remove after extraction based on several different criteria.

    Args:
        df (pd.DataFrame): The DataFrame containing the articles.
        word_count_cutoff (int): The word count threshold for flagging articles.
        whitelist (list[int]): The list of article IDs to keep. See https://bitly.cx/IlwNV.
        blacklist (dict[int, str]): The list of article IDs to remove. See https://bitly.cx/f8FIk.

    Returns:
        pd.DataFrame: The DataFrame with updated flags for articles to remove.
    """
    df = flag_no_extracted_content(df, whitelist)
    df = flag_recipe_articles(df, whitelist)
    df = flag_duplicated(df, whitelist, column="extracted_content_body")
    df = flag_duplicated(df, whitelist, column="full_url")
    df = flag_multilingual_content(df, whitelist)
    df = flag_below_word_count_cutoff(df, word_count_cutoff, whitelist)
    df = flag_articles_via_blacklist(df, blacklist)

    return df


def add_content_body(df: pd.DataFrame, excel_errors: dict[str, str]) -> pd.DataFrame:
    """

    Args:
        df (pd.DataFrame): The DataFrame containing the articles
        excel_errors (dict[str,str]): A dictionary that maps each article friendly url to the updated content body

    Returns:
        pd.DataFrame: The DataFrame with updated content body for articles with Excel errors.

    """
    for friendly_url, text in excel_errors.items():
        # Fetch rows where `friendly_url` column value must match filename
        article_index = df.index[df["friendly_url"] == friendly_url]
        # Skip if the index is empty
        if article_index.empty:
            continue
        # Assign Raw HTML content to `content_body` column
        df.loc[article_index, "content_body"] = text

    return df


def add_updated_urls(
    df: pd.DataFrame, new_urls: dict[str, dict[str, str]]
) -> pd.DataFrame:
    """

    Args:
        df (pd.DataFrame): The DataFrame containing the articles
        new_urls: A dictionary that maps each article id to the updated full_url

    Returns:
        pd.DataFrame: The DataFrame with updated full_url for articles with known 404 errors

    """
    for article_id, url in new_urls.items():
        # Fetch rows where `id` column value must match article_id
        article_index = df.index[df["id"] == article_id]
        # Skip if the index is empty
        if article_index.empty:
            continue
        # Assign updated_url to `full_url` and `full_url2` column
        df.loc[article_index, "full_url"] = url
        df.loc[article_index, "full_url2"] = url

    return df


def invert_ia_mappings(
    mappings: dict[str, dict[str, list[str]]]
) -> dict[str, dict[str, str]]:
    """

    Args:
        mappings (dict[str, dict[str, list[str]]]): A dictionary that maps the new IA mapping to the article category name for each content category

    Returns:
        dict[str, dict[str, str]]: The inverted mapping of article category name to its new IA mapping for each content category

    """
    invert_mappings = {}
    # Iterate through the new IA mapping to the article_category_names value
    for content_category, values in mappings.items():
        map_dicts = {}
        # Flip the mappings to article_category_names -> new IA map
        for ia_map, category_names in values.items():
            for category_name in category_names:
                map_dicts[category_name] = ia_map

        # Assign for each content category
        invert_mappings[content_category] = map_dicts

    return invert_mappings


def map_category_names(
    mappings: dict[str, dict[str, str]],
    df: pd.DataFrame,
    content_category_column: str,
    reference_column: str,
    new_column_name: str,
) -> pd.DataFrame:
    """

    Args:
        mappings (dict[str, dict[str, str]]): A dictionary that maps the article category name to new IA mapping for each content category
        df (pd.DataFrame): The DataFrame containing the articles
        content_category_column (str): Refer to the column name of the content category (i.e. "content_category")
        reference_column (str): Refer to the column name of the article category (i.e. "article_category_names")
        new_column_name (str): The newly created column name for the IA mappings

    Returns:
        pd.DataFrame: The DataFrame with updated IA mapping for each content category

    """
    # Initially assign the new column to None
    df[new_column_name] = None

    # Iterate through all rows in the dataframe
    for index, row in df.iterrows():
        # Get the assigned value of the "article_category_names" column
        category_string = row[reference_column]
        # Get content category of the article
        content_category = row[content_category_column]
        # Get the IA Mapping for the respective content category
        category_map = mappings.get(content_category, None)

        # Skip if the assigned value is not a string
        if not isinstance(category_string, str):
            continue

        # Replace Ampersand symbol ("&") to "and"
        category_string = category_string.replace("&", "and")

        # Assign the new value to the "article_category_names" column
        df.at[index, reference_column] = category_string
        # Remove empty stings
        categories_list = list(
            filter(lambda x: len(x.strip()) > 0, category_string.split(","))
        )

        # If the IA Mapping exists for the given content category, perform the IA Mapping for the article
        if category_map is not None:
            for ind, category_name in enumerate(categories_list):
                # Assign the new IA Mapping to the article if it exists. Otherwise, assign a null value
                result = category_map.get(category_name, None)
                categories_list[ind] = result.strip() if result is not None else None

            # Keep unique and non-null values only
            unique_categories_list = list(
                filter(lambda x: x is not None, list(set(categories_list)))
            )

            # Assign the new mappings as a joined string and assign a null value if empty string
            joined_string = " | ".join(unique_categories_list)
            df.at[index, new_column_name] = (
                joined_string.strip() if joined_string else None
            )

    return df
