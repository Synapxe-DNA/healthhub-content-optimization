"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, pipeline, node
from content_optimization.pipelines.clustering.nodes import (
 merge_ground_truth_to_data,
 connect_to_neo4j,
 clustering_weighted_embeddings,
 clustering_weighted_sim
)
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_ground_truth_to_data,
                inputs=["ground_truth_data", "params:content_contributor","weighted_embeddings"],
                outputs="merged_df_with_groundtruth",
                name="merge_ground_truth_to_data",
                tags=["weighted_embeddings","weighted_similarity"]
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
                func=clustering_weighted_embeddings,
                inputs=[
                    "merged_df_with_groundtruth",
                    "params:neo4j_config"
                ],
                outputs=["pred_cluster", "clustered_nodes", "unclustered_nodes", "cluster_articles_dict", "edges_dict", "metrics"],
                name="clustering_weighted_embeddings",
                tags=["weighted_embeddings"]
            ),
            node(
                func=clustering_weighted_sim,
                inputs=[
                    "merged_df_with_groundtruth",
                    "params:neo4j_config"
                ],
                outputs=["pred_cluster_sim", "clustered_nodes_sim", "unclustered_nodes_sim", "cluster_articles_dict_sim", "edges_dict_sim", "metrics_sim"],
                name="clustering_weighted_sim",
                tags=["weighted_similarity"]

            )
        ]
    )
