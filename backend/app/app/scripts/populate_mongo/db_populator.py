import pandas as pd
from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.edge import Edge
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    EdgeDocument,
    GroupDocument,
)
from beanie import init_beanie
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClient


class DBPopulater:
    def __init__(
        self,
        mongo_connector: DbConnector,
        articles_file_path,
        edges_file_path,
        cluster_file_path,
    ):
        self.mongo_connector = mongo_connector
        self.articles_file_path = articles_file_path
        self.edges_file_path = edges_file_path
        self.cluster_file_path = cluster_file_path

    async def init_db(self):
        await self.mongo_connector.connect()

    async def populate_articles(self):
        await self.init_db()
        articles_df = pd.read_parquet(self.articles_file_path)

        articles_df = articles_df.fillna(
            {
                column: ""
                for column in articles_df.select_dtypes(include=["object"]).columns
            }
        ).fillna(
            {
                column: -1
                for column in articles_df.select_dtypes(
                    include=["float64", "int64"]
                ).columns
            }
        )

        articles_df = articles_df[
            articles_df["pr_name"].str.contains("Health Promotion Board")
        ]
        articles_df["keywords"] = articles_df["keywords"].apply(
            lambda x: x.split(",") if x else []
        )
        articles_df["keywords"] = articles_df["keywords"].apply(
            lambda x: [e.strip() for e in x if e != ""]
        )

        articles = [
            Article(
                id=str(row["id"]),
                title=row["title"].strip(),
                description=row.get("category_description", "").strip(),
                pr_name=row.get("pr_name", "").strip(),
                content_category=row.get("content_category", "").strip(),
                url=row.get("full_url", "").strip(),
                date_modified=row.get("date_modified", ""),
                keywords=row.get("keywords", []),
                cover_image_url=row.get("cover_image_url", "").strip(),
                engagement_rate=row.get("engagement_rate", -1.0),
                number_of_views=row.get("page_views", -1),
                content=row.get("content_body", "").strip(),
            )
            for _, row in articles_df.iterrows()
        ]
        await self.mongo_connector.create_articles(articles)
        print(f"Inserted {len(articles)} article documents into MongoDB")

    async def populate_edges(self):
        await self.init_db()
        all_edges = []
        edges_df = pd.read_pickle(self.edges_file_path)
        for row in edges_df:
            node_1 = row.get("node_1_title")
            node_2 = row.get("node_2_title")
            articles_pair = await ArticleDocument.find(
                In(ArticleDocument.title, [node_1, node_2])
            ).to_list()

            # Assume page title is unique
            if len(articles_pair) != 2:
                raise ValueError(
                    f"Expected exactly 1 article for each of {node_1} and {node_2}, "
                    f"but found {len(articles_pair)} articles in total."
                )

            article_1, article_2 = articles_pair
            all_edges.append(
                Edge(
                    start=article_1.id, end=article_2.id, weight=row.get("edge_weight")
                )
            )
        await self.mongo_connector.create_edges(all_edges)
        print(f"Inserted {len(all_edges)} edges documents into MongoDB")

    async def populate_clusters(self):
        await self.init_db()
        cluster_pkl = pd.read_pickle(self.cluster_file_path)
        for row in cluster_pkl:
            articles_incluster = await ArticleDocument.find(
                In(ArticleDocument.title, row["titles"])
            ).to_list()
            cluster_name = "Cluster " + str(row["cluster"])
            await self.mongo_connector.create_group_from_articles(
                cluster_name, articles_incluster
            )
        print(f"Inserted {len(cluster_pkl)} cluster documents into MongoDB")
