"""
This is a boilerplate pipeline 'azure_rag'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.azure_rag.nodes import (
    filter_articles,
    process_html_tables,
    extract_content,
)

from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
            node(
                func=filter_articles,
                inputs="merged_data",
                outputs="filtered_data",
                name="filter_articles_node",
            ),
            node(
                func=process_html_tables,
                inputs="filtered_data",
                outputs="processed_data",
                name="process_html_tables_node",
            ),
            node(
                func=extract_content,
                inputs=[
                    "processed_data", 
                    "params:article_content_columns", 
                    "params:table_content_columns", 
                    ],
                outputs="data_for_saving",
                name="extract_content_node",
            )
    ])
