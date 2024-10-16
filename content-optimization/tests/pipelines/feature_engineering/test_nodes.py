import numpy as np
import pandas as pd
import pytest
from kedro.io import DataCatalog
from src.content_optimization.pipelines.feature_engineering.nodes import (
    extract_keywords,
)


@pytest.mark.parametrize(
    "model, top_n", [("all-MiniLM-L6-v2", 5), ("all-mpnet-base-v2", 2)]
)
def test_extract_keywords(catalog: DataCatalog, model: str, top_n: int):
    merged_data = catalog.load("merged_data")
    cfg = catalog.load("params:cfg")
    only_confirmed_option = catalog.load("params:selection_options.only_confirmed")
    all_option = catalog.load("params:selection_options.all")
    spacy_pipeline = catalog.load("params:keywords.spacy_pipeline")
    stop_words = catalog.load("params:keywords.stop_words")
    workers = catalog.load("params:keywords.workers")
    use_mmr = catalog.load("params:keywords.use_mmr")
    diversity = catalog.load("params:keywords.diversity")
    filtered_data_with_keywords = extract_keywords(
        merged_data,
        cfg,
        only_confirmed_option,
        all_option,
        model,
        spacy_pipeline,
        stop_words,
        workers,
        use_mmr,
        diversity,
        top_n,
    )

    # Check if output is a DataFrame
    assert isinstance(filtered_data_with_keywords, pd.DataFrame), "Expected a dataframe"
    # Check if output contains the expected columns
    assert (
        f"keywords_{model}" in filtered_data_with_keywords.columns
    ), f"Expected column `keywords_{model}` missing"
    assert (
        np.unique(
            filtered_data_with_keywords[f"keywords_{model}"].apply(lambda x: len(x))
        )[0]
        == top_n
    ), f"Unexpected number of keywords in column `keywords_{model}`"
