import pandas as pd


def select_and_rearrange_columns(
    df: pd.DataFrame,
    columns_to_keep: list[str],
    columns_to_add: list[str] | None = None,
) -> pd.DataFrame:
    # Drop all columns which have only null values
    df = df.dropna(axis=1, how="all")

    if columns_to_add is not None:
        # Add back selected columns which were dropped because they contained only null values
        df = df.reindex(columns=[*df.columns, *columns_to_add])

    # Rearrange columns to they are in order of `columns_to_keep`
    df = df[columns_to_keep]

    return df
