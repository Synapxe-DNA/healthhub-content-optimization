import pandas as pd
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    ClusterDocument,
    EdgeDocument,
)
from beanie import init_beanie
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClient


class DBPopulater:
    def __init__(
        self, mongo_connector, articles_file_path, edges_file_path, cluster_file_path
    ):
        self.mongo_connector = mongo_connector
        self.articles_file_path = articles_file_path
        self.edges_file_path = edges_file_path
        self.cluster_file_path = cluster_file_path
        self.client = AsyncIOMotorClient(
            mongo_connector._MongoConnector__connection_string
        )

    async def init_db(self):
        await init_beanie(
            database=self.client[self.mongo_connector._MongoConnector__db],
            document_models=[ArticleDocument, EdgeDocument, ClusterDocument],
        )

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
            ArticleDocument(
                title=row["title"].strip(),
                description=row.get("category_description", "").strip(),
                author=row.get("pr_name", "").strip(),
                pillar=row.get("content_category", "").strip(),
                url=row.get("full_url", "").strip(),
                updated=row.get("date_modified", ""),
                labels=row.get("keywords", []),
                cover_image_url=row.get("cover_image_url", "").strip(),
                engagement=row.get("engagement_rate", -1.0),
                views=row.get("page_views", -1),
            )
            for _, row in articles_df.iterrows()
        ]
        await ArticleDocument.insert_many(articles)
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
                EdgeDocument(
                    start=article_1, end=article_2, weight=row.get("edge_weight")
                )
            )
        await EdgeDocument.insert_many(all_edges)
        print(f"Inserted {len(all_edges)} edges documents into MongoDB")

    async def populate_clusters(self):
        await self.init_db()
        all_clusters = []
        cluster_pkl = pd.read_pickle(self.cluster_file_path)
        for row in cluster_pkl:
            articles_incluster = await ArticleDocument.find(
                In(ArticleDocument.title, row["titles"])
            ).to_list()
            match_start = await EdgeDocument.find(
                In(EdgeDocument.start.id, [a.id for a in articles_incluster])
            ).to_list()
            match_start_id_list = [e.id for e in match_start]
            match_end = await EdgeDocument.find(
                In(EdgeDocument.end.id, [a.id for a in articles_incluster])
            ).to_list()
            diff = [e for e in match_end if e.id not in match_start_id_list]
            final_edges = match_start + diff
            final_edges_dicts = [dict(e) for e in final_edges]
            all_clusters.append(
                ClusterDocument(
                    name="Cluster" + str(row["cluster"]),
                    article_ids=articles_incluster,
                    edges=final_edges_dicts,
                )
            )
        await ClusterDocument.insert_many(all_clusters)
        print(f"Inserted {len(all_clusters)} cluster documents into MongoDB")
