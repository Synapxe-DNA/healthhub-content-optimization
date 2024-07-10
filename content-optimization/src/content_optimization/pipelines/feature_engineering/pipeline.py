"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.6
"""

from content_optimization.pipelines.feature_engineering.nodes import extract_keywords
from kedro.pipeline import Pipeline, node, pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=extract_keywords,
                inputs=[
                    "merged_data",
                    "params:cfg",
                    "params:selection_options.only_confirmed",
                    "params:selection_options.all",
                    "params:keywords.stop_words",
                    "params:keywords.workers",
                    "params:keywords.use_mmr",
                    "params:keywords.diversity",
                    "params:keywords.top_n",
                ],
                outputs="filtered_data_with_keywords",
                name="extract_keywords_node",
            ),
        ]
    )
