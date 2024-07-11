"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, pipeline, node
from content_optimization.pipelines.clustering.nodes import (
 merge_ground_truth_to_data,
 clustering_weighted_embeddings,
)
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_ground_truth_to_data,
                inputs=["ground_truth_data", "params:content_contributor","weighted_embeddings"],
                outputs="merged_df_with_groundtruth",
                name="merge_ground_truth_to_data_node"
            ),
            node(
                func=clustering_weighted_embeddings,
                inputs=[
                    "merged_df_with_groundtruth",
                    "params:neo4j_config",
                    "params:sim_weightage.weight_title",
                    "params:sim_weightage.weight_cat",
                    "params:sim_weightage.weight_desc",
                    "params:sim_weightage.weight_body",
                    "params:sim_weightage.weight_combined",
                    "params:sim_weightage.weight_kws"
                ],
                outputs=["pred_cluster", "clustered_nodes", "unclustered_nodes", "cluster_articles_dict", "edges_dict", "metrics"],
                name="clustering_weighted_embeddings_node"
            )
        ]
    )
