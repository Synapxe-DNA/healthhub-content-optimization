"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""

import logging
import os
from pathlib import Path
from typing import Dict, Tuple, Union

import pandas as pd
import pyvis
from content_optimization.pipelines.clustering.utils import (
    assign_unique_numbers_to_topics,
    clear_db,
    combine_similarities,
    count_articles,
    create_graph_nodes,
    create_graph_proj,
    create_sim_edges,
    detect_community,
    drop_graph_projection,
    generate_cluster_keywords,
    get_cluster_size,
    get_clustered_nodes,
    get_unclustered_nodes,
    median_threshold,
    process_all_clusters,
    return_pred_cluster,
)
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError


def merge_ground_truth_to_data(
    ground_truth_data: pd.DataFrame,
    content_contributor: str,
    weighted_embeddings: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merges ground truth data with weighted embeddings.

    This function filters the ground truth data to include only entries that match the specified
    content contributor. It then merges this filtered ground truth data with the weighted embeddings
    dataframe based on the URL.

    Parameters:
        ground_truth_data (pd.DataFrame): DataFrame containing reference ground truth data, with columns including
            "Owner", "Page Title", "Combine Group ID", and "URL".
        content_contributor (str): The name of the content contributor to filter the ground truth data.
        weighted_embeddings (pd.DataFrame): DataFrame containing the weighted embeddings (loaded from a .pkl file) with a "full_url" column.

    Returns:
        pd.DataFrame: A merged DataFrame containing the weighted embeddings and ground truth label.
    """
    ground_truth_data = ground_truth_data[
        ground_truth_data["Owner"].str.contains(content_contributor)
    ]
    ground_truth_data = ground_truth_data[ground_truth_data["Combine Group ID"].notna()]

    ground_truth_data = ground_truth_data[["Page Title", "URL", "Combine Group ID"]]
    ground_truth_data.rename(
        columns={"Combine Group ID": "ground_truth_cluster"}, inplace=True
    )

    # merge with ground truth
    articles_df = pd.merge(
        weighted_embeddings,
        ground_truth_data,
        how="left",
        left_on="full_url",
        right_on="URL",
    )
    return articles_df


def generate_clusters(
    merged_df_with_groundtruth: pd.DataFrame,
    neo4j_config: Dict[str, str],
    weight_title: float,
    weight_cat: float,
    weight_desc: float,
    weight_body: float,
    weight_combined: float,
    weight_kws: float,
    set_threshold: Union[None, float],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generates the first level of clustering using graph-based method

    This function takes in a Dataframe of documents (merged_df_with_groundtruth), connects to a Neo4j database,
    creates graph nodes for each document, compute similarity scores between articles for each feature, combines similarities based on various weights,
    and detects communities via louvain community detection to form clusters.

    It returns the predicted clusters, clustered nodes, unclustered nodes, clustering metrics and cluster size for first level clustering.

    Parameters:
    merged_df_with_groundtruth (pd.DataFrame): DataFrame containing the documents with ground truth.
    neo4j_config (dict): Configuration dictionary for connecting to Neo4j. Should contain keys 'uri' and 'database'.
                         Ensure `conf/base/credentials.yml` has `neo4j_credentials` with `username` and `password`
    weight_title (float): Weight for the title similarity. Value should come from `parameters_clustering.yml`.
    weight_cat (float): Weight for the category similarity. Value should come from `parameters_clustering.yml`.
    weight_desc (float): Weight for the meta description similarity. Value should come from `parameters_clustering.yml`.
    weight_body (float): Weight for the content body similarity. Value should come from `parameters_clustering.yml`.
    weight_combined (float): Weight for the combined embeddings similarity. Value should come from `parameters_clustering.yml`.
    weight_kws (float): Weight for the keywords similarity. Value should come from `parameters_clustering.yml`.
    set_threshold (Union[None, float]): Threshold for clustering. If None, it is set based on the median threshold of combined similarities.

    Returns:
    first_level_pred_cluster (pd.DataFrame): DataFrame of predicted clusters.
    first_level_clustered_nodes (pd.DataFrame): DataFrame of nodes that were clustered.
    first_level_unclustered_nodes (pd.DataFrame): DataFrame of nodes that were not clustered.
    first_level_metrics (pd.DataFrame): DataFrame containing clustering metrics. Including no. of clusters, min & max cluster size, no. of unclustered articles and each of the weights.
    first_level_cluster_size (pd.DataFrame): DataFrame containing the size of each cluster in bins of size 5.

    Raises:
    Neo4jError: If an error occurs with Neo4j database operations.

    """
    conf_path = str(str(Path(os.getcwd()) / settings.CONF_SOURCE))
    config_loader = OmegaConfigLoader(conf_source=conf_path)
    credentials = config_loader["credentials"]

    neo4j_auth = {
        "uri": neo4j_config["uri"],
        "auth": (
            credentials["neo4j_credentials"]["username"],
            credentials["neo4j_credentials"]["password"],
        ),
        "database": neo4j_config["database"],
    }

    documents = merged_df_with_groundtruth.to_dict(orient="records")
    print(f"Number of articles: {len(documents)}")

    try:
        with GraphDatabase.driver(**neo4j_auth) as driver:
            with driver.session() as session:
                session.execute_write(clear_db)  # Clear the database
                for doc in documents:
                    session.execute_write(create_graph_nodes, doc)
                combined_similarities = combine_similarities(
                    session,
                    weight_title,
                    weight_cat,
                    weight_desc,
                    weight_body,
                    weight_combined,
                    weight_kws,
                )
                if set_threshold:
                    threshold = set_threshold
                else:
                    threshold = median_threshold(combined_similarities)
                session.execute_write(
                    create_sim_edges, combined_similarities, threshold
                )
                session.execute_write(drop_graph_projection)
                session.execute_write(create_graph_proj)
                session.execute_write(detect_community)
                first_level_pred_cluster = session.execute_read(return_pred_cluster)
                first_level_clustered_nodes = session.execute_read(get_clustered_nodes)
                first_level_unclustered_nodes = session.execute_read(
                    get_unclustered_nodes
                )
                cluster_article_count = session.execute_read(count_articles)
    except (DriverError, Neo4jError) as e:
        logging.error(f"Neo4j error occurred: {e}")
        raise

    first_level_cluster_size = get_cluster_size(
        first_level_pred_cluster, column_name="cluster"
    )

    min_count = cluster_article_count[cluster_article_count["article_count"] > 1][
        "article_count"
    ].min()
    max_count = cluster_article_count["article_count"].max()
    num_clusters = len(
        cluster_article_count[cluster_article_count["article_count"] != 1]
    )
    unclustered_count = (cluster_article_count["article_count"] == 1).sum()

    first_level_metrics = pd.DataFrame(
        {
            "Threshold": [threshold],
            "Title Weight": [weight_title],
            "Category Weight": [weight_cat],
            "Meta Description Weight": [weight_desc],
            "Keywords Weight": [weight_kws],
            "Content Body Weight": [weight_body],
            "Combined Embeddings Weight": [weight_combined],
            "Number of clusters": [num_clusters],
            "Min cluster size": [min_count],
            "Max cluster size": [max_count],
            "Number of articles not clustered": [unclustered_count],
        }
    )
    return (
        first_level_pred_cluster,
        first_level_clustered_nodes,
        first_level_unclustered_nodes,
        first_level_metrics,
        first_level_cluster_size,
    )


def generate_subclusters(
    weighted_embeddings: pd.DataFrame,
    first_level_pred_cluster: pd.DataFrame,
    umap_parameters: Dict,
    size_threshold: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate subclusters from the first level of clustering using BERTopic.

    This function processes the given clusters and embeddings to perform a second level of clustering
    on clusters that have more than 10 elements. It merges the resulting subclusters with the original
    predictions and assigns unique topic numbers to them. Additionally, it generates cluster keywords
    for clusters that did not undergo the second-level clustering but have more than one element.

    Parameters:
    ----------
    weighted_embeddings (pd.DataFrame): A DataFrame containing the weighted embeddings with 'id' and 'extracted_content_body_embeddings' columns.
    first_level_pred_cluster (pd.DataFrame): A DataFrame containing the predicted clusters with 'id' and 'cluster' columns.
    umap_parameters (Dict): A dictionary of UMAP parameters (n_neighbors, n_components) to be used for the clustering process.
    size_threshold (float): The minimum number of articles a cluster must have to proceed with subclustering.

    Returns:
    -------
    final_predicted_cluster (pd.DataFrame): A DataFrame with the updated clusters, including the new subclusters and cluster keywords.
    final_cluster_size (pd.DataFrame): DataFrame containing the size of each cluster in bins of size 5.
    final_metrics (pd.DataFrame): DataFrame containing clustering metrics. Including no. of clusters, min & max cluster size and no. of unclustered articles.
    """
    cluster_size_count = first_level_pred_cluster.cluster.value_counts()
    to_keep = cluster_size_count[cluster_size_count > size_threshold].index
    cluster_morethan_threshold = first_level_pred_cluster[
        first_level_pred_cluster.cluster.isin(to_keep)
    ]
    cluster_morethan_threshold_embeddings = pd.merge(
        cluster_morethan_threshold,
        weighted_embeddings[["id", "extracted_content_body_embeddings"]],
        how="left",
        on="id",
    )

    print(
        "No. of clusters to go through 2nd level clustering: ",
        cluster_morethan_threshold.cluster.nunique(),
    )
    final_result_df = process_all_clusters(
        cluster_morethan_threshold_embeddings, umap_parameters
    )
    final_result_df_with_numbers = assign_unique_numbers_to_topics(
        final_result_df, first_level_pred_cluster
    )
    new_cluster_to_merge = final_result_df_with_numbers[
        ["id", "top_5_kws", "Assigned Topic Number"]
    ]
    new_cluster_to_merge.columns = ["id", "cluster_kws", "new_cluster"]
    final_predicted_cluster = pd.merge(
        first_level_pred_cluster, new_cluster_to_merge, how="left", on="id"
    )
    final_predicted_cluster["new_cluster"] = (
        final_predicted_cluster["new_cluster"]
        .fillna(final_predicted_cluster["cluster"])
        .apply(int)
    )

    # Generate cluster kws for those that did not undergo bertopic (cluster_kws is na) & cluster size > 1 (cluster_mt_1)
    unique_new_clusters = final_predicted_cluster["new_cluster"].value_counts()
    cluster_mt_1 = unique_new_clusters[unique_new_clusters > 1].index
    df_cluster_kws_na = final_predicted_cluster[
        final_predicted_cluster["new_cluster"].isin(cluster_mt_1)
        & final_predicted_cluster["cluster_kws"].isna()
    ]
    cluster_kws_dict = generate_cluster_keywords(df_cluster_kws_na)
    final_predicted_cluster["cluster_kws"] = final_predicted_cluster[
        "cluster_kws"
    ].fillna(final_predicted_cluster["new_cluster"].map(cluster_kws_dict))
    final_cluster_size = get_cluster_size(
        final_predicted_cluster, column_name="new_cluster"
    )

    value_count_cluster_size = final_predicted_cluster["new_cluster"].value_counts()
    min_count = value_count_cluster_size[value_count_cluster_size != 1].min()
    max_count = value_count_cluster_size.max()
    num_clusters = (value_count_cluster_size[value_count_cluster_size != 1] != 1).sum()
    unclustered_count = (value_count_cluster_size == 1).sum()

    final_metrics = pd.DataFrame(
        {
            "Number of clusters": [num_clusters],
            "Min cluster size": [min_count],
            "Max cluster size": [max_count],
            "Number of articles not clustered": [unclustered_count],
        }
    )

    return final_predicted_cluster, final_cluster_size, final_metrics


def update_edges_dataframe(
    first_level_clustered_nodes: pd.DataFrame, final_predicted_cluster: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Update the edges DataFrame with new clusters and filter out unclustered nodes.

    This function updates the edges DataFrame (first_level_clustered_nodes) with new cluster assignments (final_predicted_cluster) and keywords from the updated
    prediction clusters. It also identifies nodes that remain unclustered (single article clusters)
    and prepares a DataFrame for these unclustered nodes with relevant columns.

    Parameters:
    ----------
    first_level_clustered_nodes (pd.DataFrame):
        A DataFrame containing the original clustered nodes with columns:
        - node_1_id: ID of the first node
        - node_2_id: ID of the second node
        - other columns as needed

    final_predicted_cluster (pd.DataFrame):
        A DataFrame containing the updated prediction clusters with columns:
        - id: Node ID
        - title: Title of the node
        - new_cluster: New cluster assignment
        - cluster_kws: Keywords associated with the cluster
        - url: URL of the node (optional, will be dropped)
        - cluster: First level cluster assignment (optional, will be dropped)
        - body_content: Content of the node (optional, will be dropped)

    Returns:
    -------
    final_unclustered_nodes (pd.DataFrame):
        A DataFrame containing the nodes that remain unclustered, with columns:
        - node_id: ID of the unclustered node
        - node_title: Title of the unclustered node
        - node_community: Community assignment of the unclustered node

    final_clustered_nodes (pd.DataFrame):
        A DataFrame containing the updated clustered nodes with new cluster assignments and keywords, filtered to remove rows with missing keywords. Columns include:
        - node_1_id: ID of the first node
        - node_2_id: ID of the second node
        - node_1_pred_cluster_new: New predicted cluster for the first node
        - node_2_pred_cluster_new: New predicted cluster for the second node
        - other columns from the merged DataFrame
    """
    unique_new_clusters = final_predicted_cluster["new_cluster"].value_counts()
    single_article_cluster = unique_new_clusters[unique_new_clusters == 1].index
    group_article_cluster = unique_new_clusters[unique_new_clusters > 1].index
    unclustered_df = final_predicted_cluster[
        final_predicted_cluster["new_cluster"].isin(single_article_cluster)
    ]
    unclustered_df = unclustered_df.rename(
        columns={
            "id": "node_id",
            "title": "node_title",
            "new_cluster": "node_community",
        }
    )
    final_unclustered_nodes = unclustered_df.drop(
        columns=["url", "cluster", "body_content", "cluster_kws"]
    )

    clustered_df_new = pd.merge(
        first_level_clustered_nodes,
        final_predicted_cluster[["id", "new_cluster", "cluster_kws"]],
        left_on="node_1_id",
        right_on="id",
        how="left",
    ).merge(
        final_predicted_cluster[["id", "new_cluster", "cluster_kws"]],
        left_on="node_2_id",
        right_on="id",
        how="left",
        suffixes=("_1", "_2"),
    )

    final_clustered_nodes = clustered_df_new.drop(
        columns=["id_1", "id_2", "node_1_pred_cluster", "node_2_pred_cluster"]
    )
    final_clustered_nodes = final_clustered_nodes.rename(
        columns={
            "new_cluster_1": "node_1_pred_cluster_new",
            "new_cluster_2": "node_2_pred_cluster_new",
            "cluster_kws_1": "node_1_cluster_kws",
            "cluster_kws_2": "node_2_cluster_kws",
        }
    )
    final_clustered_nodes = final_clustered_nodes[
        final_clustered_nodes["node_1_pred_cluster_new"].isin(group_article_cluster)
        | final_clustered_nodes["node_2_pred_cluster_new"].isin(group_article_cluster)
    ]

    return final_unclustered_nodes, final_clustered_nodes


def cluster_viz(
    final_clustered_nodes: pd.DataFrame, final_unclustered_nodes: pd.DataFrame
):
    """
    Visualize clustered and unclustered nodes using pyvis.

    This function creates an interactive network graph visualization for clustered and unclustered nodes.
    Clustered nodes are connected by edges, and each node is annotated with its predicted group and group keywords.
    Unclustered nodes are displayed without connections.

    Parameters:
    ----------
    final_clustered_nodes (pd.DataFrame):
        A DataFrame containing the clustered nodes with columns:
        - node_1_title: Title of the first node
        - node_2_title: Title of the second node
        - node_1_pred_cluster_new: Predicted cluster for the first node
        - node_2_pred_cluster_new: Predicted cluster for the second node
        - cluster_kws_1: Keywords for the first node's cluster
        - cluster_kws_2: Keywords for the second node's cluster
        - edge_weight: Weight of the edge connecting the nodes

    final_unclustered_nodes (pd.DataFrame):
        A DataFrame containing the unclustered nodes with columns:
        - node_title: Title of the unclustered node

    Returns:
    -------
    None
        The function saves the interactive network graph as an HTML file at "data/07_model_output/neo4j_cluster_viz.html" and does not return any value.
    """
    clustered_df = final_clustered_nodes.copy()
    unclustered_df = final_unclustered_nodes.copy()

    visual_graph = pyvis.network.Network(select_menu=True, filter_menu=True)

    # Add nodes-nodes pair
    for _, row in clustered_df.iterrows():
        # Add nodes
        visual_graph.add_node(
            row["node_1_title"],
            label=row["node_1_title"],
            title=f"Predicted group: {row['node_1_pred_cluster_new']}\nGroup keywords: {row['node_1_cluster_kws']}\nTitle: {row['node_1_title']}",
            group=row["node_1_pred_cluster_new"],
        )
        visual_graph.add_node(
            row["node_2_title"],
            label=row["node_2_title"],
            title=f"Predicted group: {row['node_2_pred_cluster_new']}\nGroup keywords: {row['node_2_cluster_kws']}\nTitle: {row['node_2_title']}",
            group=row["node_2_pred_cluster_new"],
        )

        # Add edges
        visual_graph.add_edge(
            row["node_1_title"],
            row["node_2_title"],
            title=f"Edge Weight: {row['edge_weight']}",
        )

    # Add solo nodes
    for _, row in unclustered_df.iterrows():
        visual_graph.add_node(
            row["node_title"],
            label=row["node_title"],
            title=f"Predicted group: No Community\nTitle: {row['node_title']}",
        )

    return visual_graph.show(
        "data/07_model_output/neo4j_cluster_viz.html", notebook=False
    )
