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
import logging
import pyvis
from content_optimization.pipelines.clustering.utils import(
    clear_db,
    create_graph_nodes,
    combine_similarities,
    median_threshold,
    create_sim_edges,
    drop_graph_projection,
    create_graph_proj,
    detect_community,
    get_clustered_nodes,
    get_unclustered_nodes,
    return_pred_cluster,
    get_cluster_size,
    generate_cluster_keywords,
    count_articles,
    return_by_cluster
)

def merge_ground_truth_to_data(ground_truth_data, content_contributor, weighted_embeddings,category_name, filtered_data):
    ground_truth_data = ground_truth_data[ground_truth_data["Owner"].str.contains(content_contributor)]
    ground_truth_data = ground_truth_data[["Page Title", "Combine Group ID", "URL"]]
    ground_truth_data = ground_truth_data[ground_truth_data["Combine Group ID"].notna()]

    ground_truth_data = ground_truth_data[["Page Title", "URL", "Combine Group ID"]]
    ground_truth_data.rename(columns={"Combine Group ID": "ground_truth_cluster"}, inplace=True)
    
    # merge with ground truth
    articles_df = pd.merge(
        weighted_embeddings,
        ground_truth_data,
        how="left",
        left_on="full_url",
        right_on="URL",
    )

    if category_name:
        article_cat_df = filtered_data[['id','article_category_names']].copy()
        article_cat_df['article_category_names'] = article_cat_df['article_category_names'].apply(lambda x: x.strip(',') if str(x)!='None' else x)
        article_cat_df['article_category_names'] = article_cat_df['article_category_names'].apply(lambda x: x.split(',') if str(x)!='None' else [None])

        id_in_category = article_cat_df[article_cat_df['article_category_names'].apply(lambda x: category_name in x)]

        articles_df = pd.merge(id_in_category, articles_df, how='left', on='id')
        print(id_in_category.shape[0] == articles_df.shape[0])
        print(articles_df)
    return articles_df

def clustering_weighted_embeddings(merged_df_with_groundtruth, neo4j_config, weight_title, weight_cat, weight_desc, weight_body, weight_combined, weight_kws,set_threshold):
    conf_path = str(str(Path(os.getcwd()) / settings.CONF_SOURCE))
    config_loader = OmegaConfigLoader(conf_source=conf_path)
    credentials = config_loader["credentials"]

    neo4j_auth = {
        "uri": neo4j_config['uri'],
        "auth": (credentials['neo4j_credentials']['username'], credentials['neo4j_credentials']['password']),
        "database": neo4j_config['database'],
    }

    documents = merged_df_with_groundtruth.to_dict(orient="records")
    print(f"Number of articles: {len(documents)}")

    try: 
        with GraphDatabase.driver(**neo4j_auth) as driver:
            with driver.session() as session:
                session.execute_write(clear_db)  # Clear the database
                for doc in documents:
                    session.execute_write(create_graph_nodes, doc)
                combined_similarities = combine_similarities(session, weight_title, weight_cat, weight_desc, weight_body, weight_combined, weight_kws)
                if set_threshold:
                    threshold = set_threshold
                else:
                    threshold = median_threshold(combined_similarities)
                session.execute_write(create_sim_edges, combined_similarities, threshold)
                session.execute_write(drop_graph_projection)
                session.execute_write(create_graph_proj)
                session.execute_write(detect_community)
                pred_cluster = session.execute_read(return_pred_cluster)
                clustered_nodes = session.execute_read(get_clustered_nodes)
                unclustered_nodes = session.execute_read(get_unclustered_nodes)
                cluster_article_count = session.execute_read(count_articles)
                cluster_articles = session.execute_read(return_by_cluster)
    except (DriverError, Neo4jError) as e:
        logging.error(f"Neo4j error occurred: {e}")
        raise

    cluster_size = get_cluster_size(pred_cluster)
    cluster_keywords_dict = generate_cluster_keywords(pred_cluster)

    min_count = cluster_article_count[cluster_article_count["article_count"] > 1][
    "article_count"
    ].min()
    max_count = cluster_article_count["article_count"].max()
    num_clusters = (cluster_article_count["article_count"] != 1).sum()
    unclustered_count = (cluster_article_count["article_count"] == 1).sum()

    cluster_articles["cluster_keywords"] = cluster_articles["cluster"].apply(lambda x, d=cluster_keywords_dict: d[x] if x in d else [])
    cluster_articles_pkl = cluster_articles.to_dict(orient='records')

    clustered_nodes["node_1_cluster_kws"] = clustered_nodes["node_1_pred_cluster"].apply(lambda x, d=cluster_keywords_dict: d[x] if x in d else [])
    clustered_nodes["node_2_cluster_kws"] = clustered_nodes["node_2_pred_cluster"].apply(lambda x, d=cluster_keywords_dict: d[x] if x in d else [])

    edges_in_same_cluster = clustered_nodes[clustered_nodes["node_1_pred_cluster"] == clustered_nodes["node_2_pred_cluster"]]
    edges = edges_in_same_cluster[["node_1_id", "node_2_id", "node_1_title", "node_2_title", "edge_weight"]]
    edges_pkl = edges.to_dict(orient='records')

    metrics_df = pd.DataFrame(
    {
        # "Model": [model_name],
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
    print(metrics_df)
    return pred_cluster, clustered_nodes, unclustered_nodes, cluster_articles_pkl, edges_pkl, metrics_df, cluster_size

def cluster_viz(
    clustered_nodes: pd.DataFrame,
    unclustered_nodes: pd.DataFrame
):
    clustered_df = clustered_nodes.copy()
    unclustered_df = unclustered_nodes.copy()
 
    visual_graph = pyvis.network.Network(select_menu=True, filter_menu=True)
 
    # Add nodes-nodes pair
    for _, row in clustered_df.iterrows():
        # Add nodes
        visual_graph.add_node(
            row["node_1_title"],
            label=row["node_1_title"],
            title=f"Predicted group: {row['node_1_pred_cluster']}\nGroup keywords: {row['node_1_cluster_kws']}\nTitle: {row['node_1_title']}",
            group=row["node_1_pred_cluster"],
        )
        visual_graph.add_node(
            row["node_2_title"],
            label=row["node_2_title"],
            title=f"Predicted group: {row['node_2_pred_cluster']}\nGroup keywords: {row['node_2_cluster_kws']}\nTitle: {row['node_2_title']}",
            group=row["node_2_pred_cluster"],
        )
 
        # Add edge
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
 
    return visual_graph.show("data/07_model_output/neo4j_cluster_viz.html", notebook=False)
 