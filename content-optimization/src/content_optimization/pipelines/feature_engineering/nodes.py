"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.6
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from kedro.framework.session import KedroSession
from kedro.io.core import DatasetError
from keybert import KeyBERT


def generate_doc_and_word_embeddings(
    merged_data: pd.DataFrame,
    cfg: dict[str, Any],
    only_confirmed_option: list[str],
    all_option: list[str],
    keyphrase_ngram_range: list[int, int],
    min_df: int,
    stop_words: str,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Generate the document and word embeddings for keywords extraction.

    Args:
        merged_data (pd.DataFrame): The DataFrame containing the merged data.
        cfg (dict[str, Any]): The configuration dictionary containing the options to subset the merged data.
        only_confirmed_option (list[str]): The list of confirmed content categories if option is `only_confirmed`.
        all_option (list[str]): The list of all content categories if option is `all`.
        keyphrase_ngram_range (list[int, int]): The range of n-grams for keyphrases extraction.
        min_df (int): The minimum document frequency for keyphrase extraction.
        stop_words (str): The stop words to be used for keyphrase extraction.
        use_mmr (bool): Flag indicating whether to use Maximal Marginal Relevance.
        diversity (float): The diversity parameter for keyphrase extraction.
        top_n (int): The number of top keyphrases to extract.

    Returns:
        tuple[pd.DataFrame, np.ndarray, np.ndarray]:
            The tuple containing the DataFrame filtered by content categories, content provider and non-flagged articles,
            along with the array of document and word embeddings for keyword extraction.
    """
    option = cfg["option"]
    contributor = cfg["contributor"]  # TODO: To allow for options other than HPB
    to_remove = cfg["to_remove"]

    # Subset the merged data based on the content categories provided as option
    if option == "only_confirmed":
        assert set(only_confirmed_option).issubset(
            set(all_option)
        ), "Invalid option(s). Please ensure selected content categories exist."
        filtered_data = merged_data.query("content_category in @only_confirmed_option")
    elif option == "all":
        filtered_data = merged_data.copy()
    else:
        assert (
            option in all_option
        ), "Invalid option. Please ensure selected content category exists."
        filtered_data = merged_data.query("content_category == @option")

    # To remove flagged articles or not and to subset by contributor
    if to_remove:
        filtered_data = filtered_data.query(
            f"pr_name == '{contributor}' and to_remove == {not to_remove}"
        ).reset_index(drop=True)
    else:
        filtered_data = filtered_data.query(f"pr_name == '{contributor}'").reset_index(
            drop=True
        )

    # Check if we already have the `doc_embeddings` and `word_embeddings` saved in the catalog
    with KedroSession.create(project_path=Path.cwd()) as session:
        context = session.load_context()
        catalog = context.catalog

    try:
        # If they already exists, load the saved embeddings
        doc_embeddings = catalog.load("doc_embeddings")
        word_embeddings = catalog.load("word_embeddings")
        print("Loading...")
    except (DatasetError, KeyError):
        print("Generating...")
        kw_model = KeyBERT()
        # Extract the raw content body text
        docs = filtered_data["extracted_content_body"].to_list()
        doc_embeddings, word_embeddings = kw_model.extract_embeddings(
            docs,
            keyphrase_ngram_range=tuple(keyphrase_ngram_range),
            min_df=min_df,
            stop_words=stop_words,
        )

    return filtered_data, doc_embeddings, word_embeddings


def extract_keywords(
    filtered_data: pd.DataFrame,
    doc_embeddings: np.ndarray,
    word_embeddings: np.ndarray,
    keyphrase_ngram_range: list[int, int],
    min_df: int,
    stop_words: str,
    use_mmr: bool,
    diversity: float,
    top_n: int,
) -> pd.DataFrame:
    """
    Extract keywords using KeyBERT model based on the provided parameters and
    return the DataFrame with the added `keybert_keywords` column containing the keywords.

    Args:
        filtered_data (pd.DataFrame): The dataframe containing the extracted content body.
        doc_embeddings (np.ndarray): The document embeddings.
        word_embeddings (np.ndarray): The word embeddings.
        keyphrase_ngram_range (list[int, int]): The range of n-grams for keyphrases extraction.
        min_df (int): The minimum document frequency for keyphrase extraction.
        stop_words (str): The stop words to be used for keyphrase extraction.
        use_mmr (bool): Whether to use Maximal Marginal Relevance (MMR) for keyphrase extraction.
        diversity (float): The diversity parameter for keyphrase extraction.
        top_n (int): The number of top keywords to extract.

    Returns:
        pd.DataFrame: The dataframe with the extracted keywords.
    """
    kw_model = KeyBERT()

    # Extract the raw content body text
    docs = filtered_data["extracted_content_body"].to_list()

    keywords = kw_model.extract_keywords(
        docs,
        keyphrase_ngram_range=tuple(keyphrase_ngram_range),
        min_df=min_df,
        stop_words=stop_words,
        use_mmr=use_mmr,
        diversity=diversity,
        top_n=top_n,
        doc_embeddings=doc_embeddings,
        word_embeddings=word_embeddings,
    )

    # We iterate through the keywords, and reverse the order of the keywords
    # from the closest to the most distant and taking only the keywords themselves,
    # ignoring the distances
    keywords = [[kw[0] for kw in kws[::-1]] for kws in keywords]
    # Store keywords in new column
    filtered_data_with_keywords = filtered_data.copy()
    filtered_data_with_keywords["keybert_keywords"] = keywords

    return filtered_data_with_keywords
