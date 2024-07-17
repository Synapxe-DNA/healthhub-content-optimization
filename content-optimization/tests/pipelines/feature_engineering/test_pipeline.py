"""
This is a boilerplate test file for pipeline 'feature_engineering'
generated using Kedro 0.19.6.
Please add your pipeline tests here.

Kedro recommends using `pytest` framework, more info about it can be found
in the official documentation:
https://docs.pytest.org/en/latest/getting-started.html
"""

import logging

from kedro.io import DataCatalog
from kedro.runner import SequentialRunner
from pytest import LogCaptureFixture
from src.content_optimization.pipelines.feature_engineering import (
    create_pipeline as create_fe_pipeline,
)


def test_feature_engineering_pipeline(caplog: LogCaptureFixture, catalog: DataCatalog):
    """
    A test function for the feature engineering pipeline.

    Args:
        caplog (LogCaptureFixture): The fixture for capturing logs.
        catalog (DataCatalog): The Kedro DataCatalog containing the necessary test datasets.

    Raises:
        AssertionError: If the successful run message is not found in the captured logs.
    """
    pipeline = (
        create_fe_pipeline()
        .from_nodes("extract_keywords_node")
        .to_nodes("extract_keywords_node")
    )

    # Arrange the log testing setup
    caplog.set_level(
        logging.DEBUG, logger="kedro"
    )  # Ensure all logs produced by Kedro are captured
    successful_run_msg = "Pipeline execution completed successfully."

    SequentialRunner().run(pipeline, catalog)

    assert successful_run_msg in caplog.text
