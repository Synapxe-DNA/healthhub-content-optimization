import asyncio
import os

from app.scripts.populate_mongo.db_populator import DBPopulator
from app.utils.db_connector.mongo_connector.mongo_connector import MongoConnector
from dotenv import load_dotenv

load_dotenv("./.env")


async def __main():
    conn = MongoConnector(
        username=os.getenv("MONGO_USERNAME"),
        password=os.getenv("MONGO_PASSWORD"),
        host=os.getenv("MONGO_HOST"),
        port=os.getenv("MONGO_PORT"),
        db_name="storage",
    )

    articles_file_path = os.path.join("app", "data", "merged_data.parquet")
    edges_file_path = os.path.join(
        "app", "data", "nomic-embed-text-v1.5_neo4j_edges.pkl"
    )  # To be edited
    cluster_file_path = os.path.join(
        "app", "data", "nomic-embed-text-v1.5_neo4j_predicted_clusters.pkl"
    )  # To be edited
    db_populator = DBPopulator(
        conn, articles_file_path, edges_file_path, cluster_file_path
    )

    await db_populator.populate_articles()
    await db_populator.populate_edges()
    await db_populator.populate_clusters()


def main():
    asyncio.run(__main())


if __name__ == "__main__":
    main()
