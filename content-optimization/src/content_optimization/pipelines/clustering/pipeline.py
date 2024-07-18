"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, pipeline, node
from content_optimization.pipelines.clustering.nodes import (
 merge_ground_truth_to_data,
 clustering_weighted_embeddings,
 cluster_viz
)
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_ground_truth_to_data,
                inputs=["ground_truth_data", "params:content_contributor","weighted_embeddings","params:category_name","filtered_data_with_keywords"],
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
                    "params:sim_weightage.weight_kws",
                    "params:set_threshold"
                ],
                outputs=["pred_cluster", "clustered_nodes", "unclustered_nodes", "cluster_articles_pkl", "edges_pkl", "metrics", "cluster_size"],
                name="clustering_weighted_embeddings_node"
            ),
              node(
                func=cluster_viz,
                inputs=[
                    "clustered_nodes",
                    "unclustered_nodes",
                ],
                outputs=None,
                name="cluster_viz_node"
            )
        ]
    )
