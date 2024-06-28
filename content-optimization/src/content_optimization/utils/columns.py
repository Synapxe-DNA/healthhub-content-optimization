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
