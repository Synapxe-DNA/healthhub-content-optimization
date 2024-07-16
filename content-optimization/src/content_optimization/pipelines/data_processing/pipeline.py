"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import add_contents, extract_data, merge_data, standardize_columns


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
                func=add_contents,
                inputs=["all_contents_standardized", "missing_contents"],
                outputs="all_contents_added",
                name="add_contents_node",
            ),
            node(
                func=extract_data,
                inputs=["all_contents_added", "params:word_count_cutoff"],
                outputs=["all_contents_extracted", "all_extracted_text"],
                name="extract_data_node",
            ),
            node(
                func=merge_data,
                inputs="all_contents_extracted",
                outputs="merged_data",
                name="merge_data_node",
            ),
        ]
    )
