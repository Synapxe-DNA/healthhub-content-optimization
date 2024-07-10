import logging
import pandas as pd
logging.basicConfig(level=logging.INFO)

def clear_db(tx):
    logging.info("Clearing database")
    tx.run("MATCH (n) DETACH DELETE n")

def create_graph_nodes(tx, doc):
    # logging.info("Create nodes")
    tx.run(
        """
    CREATE (d:Article {
        id: $id,
        title: $title,
        url: $url,
        content: $content,
        meta_desc: $meta_description,
        vector_body: $vector_body,
        vector_title: $vector_title,
        vector_category: $vector_category,
        vector_desc: $vector_desc,
        vector_kws: $vector_keywords,
        vector_combined: $vector_combined,
        ground_truth: $ground_truth
    })""",
        id=doc["id"],
        title=doc["title"],
        url=doc["full_url"],
        content=doc["content"],
        meta_description=doc["meta_description"],
        vector_title=doc["vector_title"],
        vector_category=doc["vector_article_category_names"],
        vector_desc=doc["vector_category_description"],
        vector_body=doc["vector_extracted_content_body"],
        vector_combined=doc["vector_combined"],
        vector_keywords=doc["vector_keywords"],
        ground_truth=doc["ground_truth_cluster"],
    )

def clustering_neo4j(tx, weight_title, weight_cat, weight_desc,weight_body,weight_combined,weight_kws):
    query = f"""
    MATCH (a:Article), (b:Article)
            WHERE a.id < b.id
            WITH a, b, gds.similarity.cosine(a.vector_title, b.vector_title) AS similarity_title,
                gds.similarity.cosine(a.vector_category, b.vector_category) AS similarity_cat,
                gds.similarity.cosine(a.vector_desc, b.vector_desc) AS similarity_desc,
                gds.similarity.cosine(a.vector_body, b.vector_body) AS similarity_body,
                gds.similarity.cosine(a.vector_kws, b.vector_kws) AS similarity_combined,
                gds.similarity.cosine(a.vector_kws, b.vector_kws) AS similarity_kws
            RETURN a.id AS node_1_id,
                b.id AS node_2_id,
                a.title AS node_1_title, 
                b.title AS node_2_title,
                a.ground_truth AS node_1_ground_truth, 
                b.ground_truth AS node_2_ground_truth,
                {weight_title}*similarity_title + {weight_cat}*similarity_cat + {weight_desc}*similarity_desc + {weight_body}*similarity_body + {weight_combined}*similarity_combined + {weight_kws}*similarity_kws AS weighted_similarity
            ORDER BY similarity_body DESC
    """
    result = tx.run(query)
    return [record for record in result]


def median_threshold(sim_result):
    df = pd.DataFrame(sim_result, columns=["node_1_id", "node_2_id", "node_1_title", "node_2_title","node_1_ground_truth", "node_2_ground_truth", "edge_weight"])
    df_filtered = df[df["node_1_ground_truth"] == df["node_2_ground_truth"]]
    threshold = df_filtered["edge_weight"].median()
    return threshold

def create_sim_edges(tx, threshold):
    logging.info("Create edges")
    tx.run(
        """
    MATCH (a:Article), (b:Article)
    WHERE a.id < b.id
    WITH a, b, gds.similarity.cosine(a.vector_body, b.vector_body) AS similarity
    WHERE similarity > $threshold
    CREATE (a)-[:SIMILAR {similarity: similarity}]->(b)
    """,
        threshold=threshold,
    )

def drop_graph_projection(tx):
    result = tx.run(
        """
    CALL gds.graph.exists('articleGraph')
    YIELD exists
    RETURN exists
    """
    )
    if result.single()["exists"]:
        tx.run("CALL gds.graph.drop('articleGraph')")

def create_graph_proj(tx):
    # logging.info("Create projection")
    tx.run(
        """
           CALL gds.graph.project(
            'articleGraph',
            'Article',
            {
                SIMILAR: {
                    properties: 'similarity'
                }
            }
           )
    """
    )

def detect_community(tx):
    # logging.info("Detect community")
    tx.run(
        """
        CALL gds.louvain.write(
        'articleGraph',
        {
            writeProperty: 'community'
        }
        )
    """
    )

def return_pred_cluster(tx):
    query = """
        MATCH (a:Article)
        RETURN a.id AS id,
            a.title AS title, 
            a.url AS url, 
            a.community AS cluster
        ORDER BY a.community
        """
    result = tx.run(query)
    df = pd.DataFrame(result.data())
    return df

def get_clustered_nodes(tx):
    query = """
        MATCH (n)-[r]->(m)
        RETURN n.id AS node_1_id,
            m.id AS node_2_id,
            n.title AS node_1_title, 
            m.title AS node_2_title,
            r.similarity AS edge_weight,
            n.ground_truth AS node_1_ground_truth,
            m.ground_truth AS node_2_ground_truth,
            n.community AS node_1_pred_cluster,
            m.community AS node_2_pred_cluster
        """
    result = tx.run(query)
    df = pd.DataFrame(result.data())
    return df

def get_unclustered_nodes(tx):
    query = """
        MATCH (n)
        WHERE NOT EXISTS ((n)--())
        RETURN n.title AS node_title,
            n.ground_truth AS node_ground_truth,
            n.community AS node_community,
            n.meta_desc AS node_meta_desc
        """
    result = tx.run(query)
    df = pd.DataFrame(result.data())
    return df

def count_articles(tx):
    query = """
        MATCH (a:Article)
        RETURN a.community AS cluster, count(a) AS article_count
        ORDER BY cluster
        """
    result = tx.run(query)
    df = pd.DataFrame(result.data())
    return df

def return_by_cluster(tx):
    """Return only clusters with more than one article"""

    query = """
    MATCH (n)
    WITH n.community AS cluster, collect(n.title) AS titles, count(n) AS count
    WHERE count > 1
    RETURN cluster, titles
    ORDER BY cluster
        """
    result = tx.run(query)
    df = pd.DataFrame(result.data())
    return df