from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.combination import Combination
from app.models.ignore import Ignore
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    ClusterDocument,
    CombinationDocument,
    EdgeDocument,
    IgnoreDocument,
)
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoConnector(DbConnector):
    """
    Class to connect to Mongo DB Instance
    """

    __connection_string: str
    __db: str
    __client: AsyncIOMotorClient
    __conn: AsyncIOMotorDatabase

    """
    Client setup
    """

    def __init__(
        self, username: str, password: str, host: str, port: str, db_name: str
    ):
        assert (
            username and password and host and port and db_name
        ), "Required params not provided!"

        self.__connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        self.__db = db_name

        self.__client = AsyncIOMotorClient(self.__connection_string)
        self.__conn = self.__client[self.__db]

    async def connect(self):
        await init_beanie(
            database=self.__conn,
            document_models=[
                ClusterDocument,
                ArticleDocument,
                EdgeDocument,
                CombinationDocument,
                IgnoreDocument,
            ],
        )

    """
    Class methods to interact with DB
    """

    async def create_clusters(self, cluster: List[Cluster]):
        for c in cluster:
            await ClusterDocument(
                name=c.name,
                article_ids=c.article_ids,
                edges=[
                    EdgeDocument(start=e.start, end=e.end, weight=e.weight)
                    for e in c.edges
                ],
            ).create()

    async def read_cluster_all(self) -> List[Cluster]:
        pass

    async def read_cluster(self, cluster_ids: List[str]) -> List[Cluster]:
        pass

    async def create_articles(self, articles: List[Article]):
        for a in articles:
            await ArticleDocument(
                id=a.id,
                title=a.title,
                description=a.description,
                author=a.author,
                pillar=a.pillar,
                url=a.url,
                labels=a.labels,
                cover_image_url=a.cover_image_url,
                engagement=a.engagement,
                views=a.views,
            ).create()

    async def read_article_all(self) -> List[Article]:
        pass

    async def read_article(self, article_ids: List[str]) -> List[Article]:
        pass

    async def create_combine(self, combination: List[Combination]):
        for c in combination:
            await CombinationDocument(name=c.name, article_ids=c.article_ids).create()

    async def read_combine_all(self) -> List[Combination]:
        pass

    async def read_combine(self, combine_ids: List[str]) -> List[Combination]:
        pass

    async def create_ignore(self, ignore: List[Ignore]):
        for o in ignore:
            await IgnoreDocument(article_id=o.article_id).create()

    async def read_ignore_all(self) -> List[Ignore]:
        pass

    async def read_ignore(self, optimisation_ids: List[str]) -> List[Ignore]:
        pass
