"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.data_processing.nodes import (
    extract_data,
    process_data,
)
from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=process_data,
                inputs=["all_contents", "params:columns_to_keep", "params:metadata"],
                outputs="all_contents_processed",
                name="process_data_node",
            ),
            node(
                func=extract_data,
                inputs=["all_contents_processed", "params:metadata"],
                outputs=["all_contents_extracted", "all_extracted_text"],
                name="extract_data_node",
            ),
        ]
    )
