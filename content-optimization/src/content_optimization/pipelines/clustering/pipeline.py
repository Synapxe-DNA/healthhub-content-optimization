"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, pipeline, node
from content_optimization.pipelines.clustering.nodes import (
 connect_to_neo4j,
 merge_ground_truth_to_data,
 clustering
)
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_ground_truth_to_data,
                inputs=["ground_truth_data", "params:content_contributor","weighted_embeddings"],
                outputs="merged_df_with_groundtruth"
            ),
            node(
                func=connect_to_neo4j,
                inputs=[
                    "params:neo4j_config",
                ],
                outputs=None,
                name="connect_neo_4j"
            ),
            node(
                func=clustering,
                inputs=[
                    "merged_df_with_groundtruth",
                    "params:neo4j_config",
                    "params:model_name"
                ],
                outputs=["pred_cluster", "clustered_nodes", "unclustered_nodes", "cluster_articles_dict", "edges_dict", "metrics"],
                name="clustering_neo4j"
            )
        ]
    )
