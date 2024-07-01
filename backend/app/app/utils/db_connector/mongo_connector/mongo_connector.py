from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.cluster import Cluster, ClusterPopulated
from app.models.combination import Combination, CombinationPopulated
from app.models.edge import Edge
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

    @staticmethod
    async def __get_ignored_ids() -> List[str]:
        ignored_ids = set()
        async for record in IgnoreDocument.find_all():
            ignored_ids.add(str(record.article_id))
        return list(ignored_ids)

    @staticmethod
    async def __get_combine_ids() -> List[str]:
        combined_ids = set()
        async for c in CombinationDocument.find_all(fetch_links=True):
            combined_ids.update([str(x.id) for x in c.article_ids])

        return list(combined_ids)

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

    async def read_cluster_all(self) -> List[ClusterPopulated]:

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        return [
            ClusterPopulated(
                id=str(c.id),
                name=c.name,
                articles=[
                    Article(
                        id=str(a.id),
                        title=a.title,
                        description=a.description,
                        author=a.author,
                        pillar=a.pillar,
                        url=a.url,
                        status=article_status(str(a.id)),
                        labels=a.labels,
                        cover_image_url=a.cover_image_url,
                        engagement=a.engagement,
                        views=a.views,
                    )
                    for a in c.article_ids
                ],
                edges=[
                    Edge(
                        start=str(e.start.to_dict()["id"]),
                        end=str(e.end.to_dict()["id"]),
                        weight=e.weight,
                    )
                    for e in c.edges
                ],
            )
            async for c in ClusterDocument.find_all(fetch_links=True)
        ]

    async def read_cluster(self, cluster_id: str) -> Cluster:
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

    async def read_article(self, article_id: str) -> Article:
        pass

    async def create_combine(self, combination: List[Combination]):
        for c in combination:
            await CombinationDocument(name=c.name, article_ids=c.article_ids).create()

    async def read_combine_all(self) -> List[CombinationPopulated]:

        return [
            CombinationPopulated(
                id=str(c.id),
                name=c.name,
                articles=[
                    Article(
                        id=str(a.id),
                        title=a.title,
                        description=a.description,
                        author=a.author,
                        pillar=a.pillar,
                        url=a.url,
                        # status=a.status,  HELP HERE!
                        labels=a.labels,
                        cover_image_url=a.cover_image_url,
                        engagement=a.engagement,
                        views=a.views,
                    )
                    for a in c.article_ids
                ],
            )
            async for c in CombinationDocument.find_all(fetch_links=True)
        ]

    async def read_combine(self, combine_id: str) -> Combination:
        pass

    async def create_ignore(self, ignore: List[Ignore]):
        for o in ignore:
            await IgnoreDocument(article_id=o.article_id).create()

    async def read_ignore_all(self) -> List[Ignore]:
        ignore_records = await IgnoreDocument.find_all().to_list()

        return [
            Ignore(id=str(i.id), article_id=str(i.article_id)) for i in ignore_records
        ]

    async def read_ignore(self, optimisation_id: str) -> Ignore:
        pass
