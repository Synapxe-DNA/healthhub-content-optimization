"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, pipeline, node
from content_optimization.pipelines.clustering.nodes import (
 merge_ground_truth_to_data,
#  connect_to_neo4j,
 clustering_weighted_embeddings,
)
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_ground_truth_to_data,
                inputs=["ground_truth_data", "params:content_contributor","weighted_embeddings"],
                outputs="merged_df_with_groundtruth",
                name="merge_ground_truth_to_data"
            ),
            node(
                func=clustering_weighted_embeddings,
                inputs=[
                    "merged_df_with_groundtruth",
                    "params:neo4j_config",
                    "params:embeddings_weightage"
                ],
                outputs=["pred_cluster", "clustered_nodes", "unclustered_nodes", "cluster_articles_dict", "edges_dict", "metrics"],
                name="clustering_weighted_embeddings"
            )
        ]
    )
