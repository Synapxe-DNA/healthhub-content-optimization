from pathlib import Path

import pytest
from kedro.config import OmegaConfigLoader
from kedro.io import DataCatalog
from kedro_datasets.pandas.parquet_dataset import ParquetDataset
from kedro_datasets.partitions.partitioned_dataset import PartitionedDataset

# Get the project root directory
project_path = Path.cwd()


@pytest.fixture
def datasets() -> dict:
    datasets = {
        "all_contents": PartitionedDataset(
            dataset="pandas.ExcelDataset",
            path=(
                project_path / "tests" / "data" / "01_raw" / "all_contents"
            ).as_posix(),
        ),
        "missing_contents": PartitionedDataset(
            dataset="text.TextDataset",
            path=(
                project_path / "tests" / "data" / "01_raw" / "missing_contents"
            ).as_posix(),
        ),
        "all_contents_standardized": PartitionedDataset(
            dataset="pandas.ParquetDataset",
            path=(
                project_path
                / "tests"
                / "data"
                / "02_intermediate"
                / "all_contents_standardized"
            ).as_posix(),
        ),
        "all_contents_added": PartitionedDataset(
            dataset="pandas.ParquetDataset",
            path=(
                project_path
                / "tests"
                / "data"
                / "02_intermediate"
                / "all_contents_added"
            ).as_posix(),
        ),
        "all_contents_extracted": PartitionedDataset(
            dataset="pandas.ParquetDataset",
            path=(
                project_path
                / "tests"
                / "data"
                / "02_intermediate"
                / "all_contents_extracted"
            ).as_posix(),
        ),
        "merged_data": ParquetDataset(
            filepath=(
                project_path / "tests" / "data" / "03_primary" / "merged_data.parquet"
            ).as_posix(),
        ),
        "filtered_data_with_keywords": ParquetDataset(
            filepath=(
                project_path
                / "tests"
                / "data"
                / "03_primary"
                / "filtered_data_with_keywords.parquet"
            ).as_posix(),
        ),
    }
    return datasets


@pytest.fixture
def parameters() -> dict:
    config_loader = OmegaConfigLoader(conf_source=".")
    parameters = config_loader["parameters"]
    return parameters


@pytest.fixture
def catalog(datasets: dict, parameters: dict) -> DataCatalog:
    # Arrange data catalog
    catalog = DataCatalog()
    catalog.add_feed_dict(
        {
            "all_contents": datasets["all_contents"],
            "missing_contents": datasets["missing_contents"],
            "params:columns_to_add": parameters["columns_to_add"],
            "params:columns_to_keep": parameters["columns_to_keep"],
            "params:default_columns": parameters["default_columns"],
            "params:word_count_cutoff": parameters["word_count_cutoff"],
            "params:whitelist": parameters["whitelist"],
            "all_contents_standardized": datasets["all_contents_standardized"],
            "all_contents_added": datasets["all_contents_added"],
            "all_contents_extracted": datasets["all_contents_extracted"],
            "merged_data": datasets["merged_data"],
            "params:cfg": parameters["cfg"],
            "params:selection_options.only_confirmed": parameters["selection_options"][
                "only_confirmed"
            ],
            "params:selection_options.all": parameters["selection_options"]["all"],
            "params:keywords.model": parameters["keywords"]["model"],
            "params:keywords.spacy_pipeline": parameters["keywords"]["spacy_pipeline"],
            "params:keywords.stop_words": parameters["keywords"]["stop_words"],
            "params:keywords.workers": parameters["keywords"]["workers"],
            "params:keywords.use_mmr": parameters["keywords"]["use_mmr"],
            "params:keywords.diversity": parameters["keywords"]["diversity"],
            "params:keywords.top_n": parameters["keywords"]["top_n"],
        }
    )
    return catalog
