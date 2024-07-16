"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import extract_keywords


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
                    "params:keywords.model",
                    "params:keywords.spacy_pipeline",
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
