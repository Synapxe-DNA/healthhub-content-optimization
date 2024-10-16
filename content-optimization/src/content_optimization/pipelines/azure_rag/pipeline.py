"""
This is a boilerplate pipeline 'azure_rag'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.azure_rag.nodes import (
    extract_content,
    filter_articles,
    process_html_tables,
)
from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=filter_articles,
                inputs=[
                    "merged_data",
                    "params:azure_blacklist",
                    "params:azure_whitelist",
                    "params:lengthy_articles",
                ],
                outputs="filtered_data_rag",
                name="filter_articles_node",
            ),
            node(
                func=process_html_tables,
                inputs=[
                    "filtered_data_rag",
                    "params:temperature",
                    "params:max_tokens",
                    "params:n_completions",
                    "params:seed",
                ],
                outputs="processed_data_rag",
                name="process_html_tables_node",
            ),
            node(
                func=extract_content,
                inputs=[
                    "processed_data_rag",
                    "params:article_content_columns",
                    "params:table_content_columns",
                ],
                outputs="json_data_rag",
                name="extract_content_node",
            ),
        ]
    )
