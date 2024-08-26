"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.data_processing.nodes import (
    add_data,
    extract_data,
    map_data,
    merge_data,
    standardize_columns,
)
from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=standardize_columns,
                inputs=[
                    "all_contents",
                    "params:columns_to_add",
                    "params:columns_to_keep",
                    "params:default_columns",
                ],
                outputs="all_contents_standardized",
                name="standardize_columns_node",
            ),
            node(
                func=add_data,
                inputs=[
                    "all_contents_standardized",
                    "missing_contents",
                    "params:updated_urls",
                ],
                outputs="all_contents_added",
                name="add_data_node",
            ),
            node(
                func=extract_data,
                inputs=[
                    "all_contents_added",
                    "params:word_count_cutoff",
                    "params:whitelist",
                    "params:blacklist",
                ],
                outputs=["all_contents_extracted", "all_extracted_text"],
                name="extract_data_node",
            ),
            node(
                func=map_data,
                inputs=[
                    "all_contents_extracted",
                    "params:l1_mappings",
                    "params:l2_mappings",
                ],
                outputs="all_contents_mapped",
                name="map_data_node",
            ),
            node(
                func=merge_data,
                inputs="all_contents_mapped",
                outputs="merged_data",
                name="merge_data_node",
            ),
        ]
    )
