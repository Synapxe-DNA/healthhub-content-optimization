import pytest
from kedro.config import OmegaConfigLoader
from kedro.io import DataCatalog
from kedro_datasets.partitions.partitioned_dataset import PartitionedDataset


@pytest.fixture
def datasets() -> dict:
    datasets = {
        "all_contents": PartitionedDataset(
            dataset="pandas.ExcelDataset",
            path="tests/data/01_raw/all_contents",
        ),
        "all_contents_standardized": PartitionedDataset(
            dataset="pandas.ParquetDataset",
            path="tests/data/02_intermediate/all_contents_standardized",
        ),
        "all_contents_extracted": PartitionedDataset(
            dataset="pandas.ParquetDataset",
            path="tests/data/02_intermediate/all_contents_extracted",
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
            "params:columns_to_add": parameters["columns_to_add"],
            "params:columns_to_keep": parameters["columns_to_keep"],
            "params:default_columns": parameters["default_columns"],
            "params:word_count_cutoff": parameters["word_count_cutoff"],
            "all_contents_standardized": datasets["all_contents_standardized"],
            "all_contents_extracted": datasets["all_contents_extracted"],
        }
    )
    return catalog
