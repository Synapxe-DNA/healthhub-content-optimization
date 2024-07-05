"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.6
"""

from typing import Any

import pandas as pd
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseTfidfVectorizer
from pytictoc import TicToc


def extract_keywords(
    merged_data: pd.DataFrame,
    cfg: dict[str, Any],
    only_confirmed_option: list[str],
    all_option: list[str],
    stop_words: str,
    workers: int,
    use_mmr: bool,
    diversity: float,
    top_n: int,
) -> pd.DataFrame:
    """
    Extract keywords using KeyBERT model based on the provided parameters and
    return the DataFrame with the added `keybert_keywords` column containing the keywords.

    Args:
        merged_data (pd.DataFrame): The DataFrame containing the merged data.
        cfg (dict[str, Any]): The configuration dictionary containing the options to subset the merged data.
        only_confirmed_option (list[str]): The list of confirmed content categories if option is `only_confirmed`.
        all_option (list[str]): The list of all content categories if option is `all`.
        stop_words (str): The stop words to be used for keyphrase extraction.
        workers (int): Number of workers for spaCy part-of-speech tagging. If set to -1, use all available worker threads of the machine.
        use_mmr (bool): Whether to use Maximal Marginal Relevance (MMR) for keyphrase extraction.
        diversity (float): The diversity parameter for keyphrase extraction.
        top_n (int): The number of top keywords to extract.

    Returns:
         pd.DataFrame: The dataframe with the extracted keywords.
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

    # Extract the raw content body text
    docs = filtered_data["extracted_content_body"].to_list()

    kw_model = KeyBERT()
    vectorizer = KeyphraseTfidfVectorizer(stop_words=stop_words, workers=workers)

    # Marginally more performant
    # See: https://github.com/MaartenGr/KeyBERT/issues/156
    with TicToc():
        counts = vectorizer.fit(docs)
        vectorizer.fit = lambda *args, **kwargs: counts

        # If keyphrase vectorizer is specified, `keyphrase_ngram_range` is ignored
        keywords = kw_model.extract_keywords(
            docs,
            use_mmr=use_mmr,
            diversity=diversity,
            top_n=top_n,
            vectorizer=vectorizer,
        )

    # We iterate through the keywords, and reverse the order of the keywords
    # from the closest to the most distant and taking only the keywords themselves,
    # ignoring the distances
    keywords = [[kw[0] for kw in kws[::-1]] for kws in keywords]
    # Store keywords in new column
    filtered_data_with_keywords = filtered_data.copy()
    filtered_data_with_keywords["keybert_keywords"] = keywords

    return filtered_data_with_keywords
