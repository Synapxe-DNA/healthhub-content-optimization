"""
This is a boilerplate pipeline 'clustering'
generated using Kedro 0.19.6
"""
import os 
from pathlib import Path
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
import pandas as pd
from content_optimization.pipelines.clustering.utils import(
    clear_db,
    create_graph_nodes,
    calculate_similarity,
    median_threshold,
    create_sim_edges,
    drop_graph_projection,
    create_graph_proj,
    detect_community,
    get_clustered_nodes,
    get_unclustered_nodes,
    return_pred_cluster,
    count_articles,
    return_by_cluster
)

def merge_ground_truth_to_data(ground_truth_data, content_contributor, weighted_embeddings):
    ground_truth = ground_truth_data
    ground_truth = ground_truth[ground_truth["Owner"].str.contains(content_contributor)]
    ground_truth = ground_truth[["Page Title", "Combine Group ID", "URL"]]
    ground_truth = ground_truth[ground_truth["Combine Group ID"].notna()]

    # Extract id from merged_data_df to ground truth
    ground_truth = pd.merge(
        ground_truth, weighted_embeddings, how="inner", left_on="URL", right_on="full_url"
    )
    ground_truth = ground_truth[["id", "Page Title", "URL", "Combine Group ID"]]
    ground_truth.rename(columns={"Combine Group ID": "ground_truth_cluster"}, inplace=True)
    # merge with ground truth
    articles_df = pd.merge(
        weighted_embeddings,
        ground_truth,
        how="inner",
        left_on="id",
        right_on="id",
    )
    return articles_df

def connect_to_neo4j(neo4j_config):
    conf_path = str(str(Path(os.getcwd()) / settings.CONF_SOURCE))
    config_loader = OmegaConfigLoader(conf_source=conf_path)
    credentials = config_loader["credentials"]

    neo4j_auth = {
        "uri": neo4j_config['uri'],
        "auth": (credentials['neo4j_credentials']['username'], credentials['neo4j_credentials']['password']),
        "database": neo4j_config['database'],
    }

    with GraphDatabase.driver(**neo4j_auth) as driver:
        try:
            driver.verify_connectivity()
            print("Connection established")
        except (DriverError, Neo4jError) as exception:
            return str(exception)
        

def clustering(merged_df_with_groundtruth, neo4j_config, model_name):
    conf_path = str(str(Path(os.getcwd()) / settings.CONF_SOURCE))
    config_loader = OmegaConfigLoader(conf_source=conf_path)
    credentials = config_loader["credentials"]

    neo4j_auth = {
        "uri": neo4j_config['uri'],
        "auth": (credentials['neo4j_credentials']['username'], credentials['neo4j_credentials']['password']),
        "database": neo4j_config['database'],
    }

    documents = merged_df_with_groundtruth.to_dict(orient="records")
    with GraphDatabase.driver(**neo4j_auth) as driver:
        with driver.session() as session:
            session.execute_write(clear_db)  # Clear the database
            for doc in documents:
                session.execute_write(create_graph_nodes, doc)
            sim_result = session.execute_write(calculate_similarity)
            threshold = median_threshold(sim_result)
            session.execute_write(create_sim_edges, threshold)
            session.execute_write(drop_graph_projection)
            session.execute_write(create_graph_proj)
            session.execute_write(detect_community)
            pred_cluster = session.execute_read(return_pred_cluster)
            clustered_nodes = session.execute_read(get_clustered_nodes)
            unclustered_nodes = session.execute_read(get_unclustered_nodes)
            cluster_article_count = session.execute_read(count_articles)
            cluster_articles = session.execute_read(return_by_cluster)

    min_count = cluster_article_count[cluster_article_count["article_count"] > 1][
    "article_count"
    ].min()
    max_count = cluster_article_count["article_count"].max()
    num_clusters = (cluster_article_count["article_count"] != 1).sum()
    unclustered_count = (cluster_article_count["article_count"] == 1).sum()

    cluster_articles_dict = cluster_articles.to_dict(orient='records')

    edges_in_same_cluster = clustered_nodes[clustered_nodes["node_1_pred_cluster"] == clustered_nodes["node_2_pred_cluster"]]
    edges = edges_in_same_cluster[["node_1_title", "node_2_title", "edge_weight"]]
    edges_dict = edges.to_dict(orient='records')

    metrics_df = pd.DataFrame(
    {
        "Model": [model_name],
        "Threshold": [threshold],
        "Number of clusters": [num_clusters],
        "Min cluster size": [min_count],
        "Max cluster size": [max_count],
        "Number of articles not clustered": [unclustered_count],
    }
)

    return pred_cluster, clustered_nodes, unclustered_nodes, cluster_articles_dict, edges_dict, metrics_df
