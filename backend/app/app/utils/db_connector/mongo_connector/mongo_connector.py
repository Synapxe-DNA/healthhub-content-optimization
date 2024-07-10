from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.cluster import Cluster, ClusterPopulated
from app.models.combination import Combination, CombinationPopulated
from app.models.edge import Edge
from app.models.ignore import Optimise
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    ClusterDocument,
    CombinationDocument,
    EdgeDocument,
    IgnoreDocument,
)
from beanie import init_beanie
from bson.objectid import ObjectId
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
        """
        Connection parameters to configure `MongoConnector`
        :param username: MongoDb Username
        :param password: MongoDb Password
        :param host: Host IP address or URL
        :param port: Port number exposed for Mongo
        :param db_name: Name of the database on MongoDb
        """
        assert (
            username and password and host and port and db_name
        ), "Required params not provided!"

        self.__connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        self.__db = db_name

        self.__client = AsyncIOMotorClient(self.__connection_string)
        self.__conn = self.__client[self.__db]

    async def connect(self):
        """
        Method to initialise Beanie ODM
        :return:
        """
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
        """
        Method to get a unique list of all article IDs that have been ignored
        :return: List[str]
        """
        ignored_ids = set()
        async for record in IgnoreDocument.find_all(fetch_links=True):
            ignored_ids.add(str(record.article_id.id))
        return list(ignored_ids)

    @staticmethod
    async def __get_combine_ids() -> List[str]:
        """
        Method to get a unique list of all article IDs that have been added to a "combine" job
        :return: List[str]
        """
        combined_ids = set()
        async for c in CombinationDocument.find_all(fetch_links=True):
            combined_ids.update([str(x.id) for x in c.article_ids])

        return list(combined_ids)

    """
    Class methods to interact with DB
    """

    async def create_clusters(self, cluster: List[Cluster]) -> None:
        """
        Method to create (multiple) cluster documents.
        :param cluster:
        :return: None
        """
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
        """
        Method to fetch all clusters. Clusters will be populated with articles and edges.
        :return: List[ClusterPopulated]
        """

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
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
                        author=a.pr_name,
                        pillar=a.content_category,
                        url=a.url,
                        updated=a.data_modified,
                        status=article_status(str(a.id)),
                        labels=a.keywords,
                        cover_image_url=a.cover_image_url,
                        engagement=a.engagement_rate,
                        views=a.number_of_views,
                    )
                    for a in c.article_ids
                ],
                edges=[
                    Edge(
                        start=e.start.to_dict()["id"],
                        end=e.end.to_dict()["id"],
                        weight=e.weight,
                    )
                    for e in c.edges
                ],
            )
            async for c in ClusterDocument.find_all(fetch_links=True)
        ]

    async def read_cluster(self, cluster_id: str) -> ClusterPopulated:
        """
        Method to get a ClusterPopulated object from a specified cluster_id
        :param cluster_id:
        :return:
        """

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        cluster = await ClusterDocument.get(ObjectId(cluster_id), fetch_links=True)

        return ClusterPopulated(
            id=str(cluster.id),
            name=cluster.name,
            articles=[
                Article(
                    id=str(a.id),
                    title=a.title,
                    description=a.description,
                    author=a.pr_name,
                    pillar=a.content_category,
                    url=a.url,
                    updated=a.data_modified,
                    status=article_status(str(a.id)),
                    labels=a.keywords,
                    cover_image_url=a.cover_image_url,
                    engagement=a.engagement_rate,
                    views=a.number_of_views,
                )
                for a in cluster.article_ids
            ],
            edges=[
                Edge(
                    start=e.start.to_dict()["id"],
                    end=e.end.to_dict()["id"],
                    weight=e.weight,
                )
                for e in cluster.edges
            ],
        )

    async def create_articles(self, articles: List[Article]):
        """
        Method to insert (multiple) articles into Mongo DB.
        :param articles:
        :return:
        """

        for a in articles:
            await ArticleDocument(
                id=a.id,
                title=a.title,
                description=a.description,
                author=a.pr_name,
                pillar=a.content_category,
                url=a.url,
                labels=a.keywords,
                cover_image_url=a.cover_image_url,
                engagement=a.engagement_rate,
                views=a.number_of_views,
            ).create()

    async def read_article_all(self) -> List[Article]:
        """
        Method to retrieve all articles in the database.
        :return:
        """

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        return [
            Article(
                id=str(a.id),
                title=a.title,
                description=a.description,
                author=a.pr_name,
                pillar=a.content_category,
                url=a.url,
                status=article_status(a.id),
                labels=a.keywords,
                cover_image_url=a.cover_image_url,
                engagement=a.engagement_rate,
                views=a.number_of_views,
            )
            async for a in ArticleDocument.find_all()
        ]

    async def read_article(self, article_id: str) -> Article:
        """
        Method to get a particular article by ID
        :param article_id:
        :return:
        """

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        article = await ArticleDocument.get(article_id)

        return Article(
            id=str(article.id),
            title=article.title,
            description=article.description,
            author=article.pr_name,
            pillar=article.content_category,
            url=article.url,
            updated=article.data_modified,
            status=article_status(str(article.id)),
            labels=article.keywords,
            cover_image_url=article.cover_image_url,
            engagement=article.engagement_rate,
            views=article.number_of_views,
        )

    async def create_combine(self, combination: List[Combination]):
        """
        Method to insert (multiple) Combination documents into the DB.
        :param combination:
        :return:
        """

        for c in combination:
            await CombinationDocument(name=c.name, article_ids=c.article_ids).create()

    async def read_combine_all(self) -> List[CombinationPopulated]:
        """
        Method to retrieve all records of combination jobs
        :return:
        """

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        return [
            CombinationPopulated(
                id=str(c.id),
                name=c.name,
                articles=[
                    Article(
                        id=str(a.id),
                        title=a.title,
                        description=a.description,
                        author=a.pr_name,
                        pillar=a.content_category,
                        url=a.url,
                        updated=a.data_modified,
                        status=article_status(str(a.id)),
                        labels=a.keywords,
                        cover_image_url=a.cover_image_url,
                        engagement=a.engagement_rate,
                        views=a.number_of_views,
                    )
                    for a in c.article_ids
                ],
            )
            async for c in CombinationDocument.find_all(fetch_links=True)
        ]

    async def read_combine(self, combine_id: str) -> CombinationPopulated:

        ignore_ids = await self.__get_ignored_ids()
        combined_ids = await self.__get_combine_ids()

        def article_status(_id: str) -> str:
            """
            Function to get the appropriate state for each article.
            :param _id:
            :return:
            """
            if _id in ignore_ids:
                return "IGNORED"
            if _id in combined_ids:
                return "COMBINED"
            return ""

        combine_doc = await CombinationDocument.find(
            CombinationDocument.id == ObjectId(combine_id), fetch_links=True
        ).to_list()

        # TODO [BUG] Linting fix needed
        # Linter will show that a.[attr] doesn't exist. This is due to the type hinting of the Document.find()
        # not accounting for `fetch_links=True`.
        return CombinationPopulated(
            id=str(combine_doc[0].id),
            name=combine_doc[0].name,
            articles=[
                Article(
                    id=str(a.id),
                    title=a.title,
                    description=a.description,
                    author=a.pr_name,
                    pillar=a.content_category,
                    url=a.url,
                    updated=a.data_modified,
                    status=article_status(str(a.id)),
                    labels=a.keywords,
                    cover_image_url=a.cover_image_url,
                    engagement=a.engagement_rate,
                    views=a.number_of_views,
                )
                for a in combine_doc[0].article_ids
            ],
        )

    async def create_ignore(self, ignore: List[Optimise]):
        for o in ignore:
            await IgnoreDocument(article_id=o.article_id).create()

    async def read_ignore_all(self) -> List[Optimise]:
        """
        Method to retrieve all ignored articles.
        Note: this does not return a populated Ignore as we'll probably only need the IDs
        :return:
        """
        return [
            Optimise(id=str(i.id), article_id=str(i.article_id))
            async for i in IgnoreDocument.find_all()
        ]

    async def read_ignore(self, ignore_id: str) -> Optimise:
        """
        Method to retrieve a particular ignore record.
        :param ignore_id:
        :return:
        """
        ignore = await IgnoreDocument.get(ObjectId(ignore_id))

        return Optimise(id=str(ignore.id), article_id=ignore.article_id.to_dict()["id"])
