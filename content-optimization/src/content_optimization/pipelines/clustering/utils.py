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

def calculate_similarity(tx, vector_name):
    query = f"""
    MATCH (a:Article), (b:Article)
    WHERE a.id < b.id
    RETURN a.id AS node_1_id, b.id AS node_2_id,
           gds.similarity.cosine(a.{vector_name}, b.{vector_name}) AS similarity
    """
    result = tx.run(query)
    return {(record['node_1_id'], record['node_2_id']): record['similarity'] for record in result}

def fetch_ground_truth(session):
    query = """
    MATCH (a:Article)
    RETURN a.id AS id, a.ground_truth AS ground_truth
    """
    result = session.run(query)
    ground_truth = {record['id']: record['ground_truth'] for record in result}
    return ground_truth

def combine_similarities(session, weight_title, weight_cat, weight_desc, weight_body, weight_combined, weight_kws):
    ground_truth = fetch_ground_truth(session)

    similarities_title = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_title'))
    similarities_cat = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_category'))
    similarities_desc = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_desc'))
    similarities_body = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_body'))
    similarities_combined = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_combined'))
    similarities_kws = session.execute_write(lambda tx: calculate_similarity(tx, 'vector_kws'))

    combined_similarities = []

    for key in similarities_title.keys():
        if key in similarities_cat and key in similarities_desc and key in similarities_body and key in similarities_combined and key in similarities_kws:
            node_1_ground_truth = ground_truth.get(key[0])
            node_2_ground_truth = ground_truth.get(key[1])


            combined_similarity = {
                'node_1_id': key[0],
                'node_2_id': key[1],
                'node_1_ground_truth': node_1_ground_truth,
                'node_2_ground_truth': node_2_ground_truth,
                'weighted_similarity': (
                    weight_title * similarities_title[key] +
                    weight_cat * similarities_cat[key] +
                    weight_desc * similarities_desc[key] +
                    weight_body * similarities_body[key] +
                    weight_combined * similarities_combined[key] +
                    weight_kws * similarities_kws[key]
                )
            }
            combined_similarities.append(combined_similarity)

    return combined_similarities

def median_threshold(combined_similarities):
    df = pd.DataFrame(combined_similarities)
    df = df.dropna(subset=["node_1_ground_truth", "node_2_ground_truth"])
    df_filtered = df[df["node_1_ground_truth"] == df["node_2_ground_truth"]]
    threshold = df_filtered["weighted_similarity"].median()
    return threshold

def create_sim_edges(tx, similarities, threshold):
    logging.info("Creating edges")
    for record in similarities:
        if record['weighted_similarity'] > threshold:
            tx.run(
                """
                MATCH (a:Article {id: $node_1_id}), (b:Article {id: $node_2_id})
                CREATE (a)-[:SIMILAR {similarity: $weighted_similarity}]->(b)
                """,
                node_1_id=record['node_1_id'],
                node_2_id=record['node_2_id'],
                weighted_similarity=record['weighted_similarity']
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