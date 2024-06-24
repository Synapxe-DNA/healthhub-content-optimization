"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.data_processing.nodes import preprocess_data
from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=preprocess_data,
                inputs=[
                    "all_contents",
                    "params:content_category",
                    "params:columns_to_drop",
                    "params:metadata",
                ],
                outputs=["all_contents_extracted", "all_extracted_text"],
                name="preprocess_data_node",
            ),
        ]
    )
