from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article, ArticleMeta, ArticleStatus
from app.models.cluster import Cluster
from app.models.edge import Edge
from app.models.generated_article import GeneratedArticle
from app.models.job_combine import JobCombine
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    ClusterDocument,
    EdgeDocument,
    GeneratedArticleDocument,
    IgnoreDocument,
    JobCombineDocument,
    JobOptimiseDocument,
    RemoveDocument,
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
                GeneratedArticleDocument,
                EdgeDocument,
                JobCombineDocument,
                JobOptimiseDocument,
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
            ignored_ids.add(str(record.article.id))
        return list(ignored_ids)

    @staticmethod
    async def __get_combined_ids() -> List[str]:
        """
        Method to get a unique list of all article IDs that have been combined
        :return: List[str]
        """
        combined_ids = set()
        async for record in JobCombineDocument.find_all(
            fetch_links=True
        ).original_articles:
            combined_ids.add(str(record.article_id.id))
        return list(combined_ids)

    @staticmethod
    async def __get_optimised_ids() -> List[str]:
        """
        Method to get a unique list of all article IDs that have been combined
        :return: List[str]
        """
        optimised_ids = set()
        async for record in JobOptimiseDocument.find_all(fetch_links=True):
            optimised_ids.add(str(record.original_article.id))
        return list(optimised_ids)

    @staticmethod
    async def __get_removed_ids() -> List[str]:
        """
        Method to get a unique list of all article IDs that have been removed
        :return: List[str]
        """
        removed_ids = set()
        async for record in RemoveDocument.find_all(fetch_links=True):
            removed_ids.add(str(record.original_article.id))
        return list(removed_ids)

    async def get_article_status(self, _id: str) -> str:
        """
        Method to get a article status
        """
        remove_ids = await self.__get_removed_ids()
        combined_ids = await self.__get_combined_ids()
        optimise_ids = await self.__get_optimised_ids()

        if _id in remove_ids:
            return ArticleStatus.REMOVE
        elif _id in combined_ids:
            return ArticleStatus.COMBINE
        elif _id in optimise_ids:
            return ArticleStatus.OPTIMISE
        else:
            return ArticleStatus.IGNORE

    """
    Class methods to interact with DB
    """

    async def create_cluster_from_articles(
        self, cluster_name: str, article_ids: List[str]
    ) -> str:
        """
        Method to group a cluster from existing articles
        :param cluster_name: {str} Name of cluster
        :param article_ids: {List[str]} List of IDs of articles
        :return: {str} ID of newly created cluster
        """
        cluster = ClusterDocument(name=cluster_name, article_ids=article_ids)
        await cluster.insert()
        return str(cluster.id)

    async def get_all_clusters(self) -> List[Cluster]:
        """
        Method to retrieve all clusters, populated with their respective ArticleMeta and Edges
        :return: {List[Cluster]}
        """

        return [
            Cluster(
                id=str(c.id),
                name=c.name,
                articles=[
                    ArticleMeta(
                        id=str(a.id),  # Will only be present when retrieving from DB
                        title=a.title,
                        description=a.description,
                        pr_name=a.pr_name,
                        content_category=a.content_category,
                        url=a.url,
                        status=self.get_article_status(str(a.id)),
                        data_modified=a.date_modified,
                        keywords=a.keywords,
                        cover_image_url=a.cover_image_url,
                        engagement_rate=a.engagement_rate,
                        number_of_views=a.number_of_views,
                    )
                    for a in c.article_ids
                ],
                edges=self.get_edges([str(a.id) for a in c.article_ids]),
            )
            async for c in ClusterDocument.find_all(fetch_links=True)
        ]

    async def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Method to fetch a cluster by ID.
        :param cluster_id:
        :return:
        """
        cluster = await ClusterDocument.get(cluster_id)

        return Cluster(
            id=str(cluster.id),
            name=cluster.name,
            articles=[
                ArticleMeta(
                    id=str(a.id),  # Will only be present when retrieving from DB
                    title=a.title,
                    description=a.description,
                    pr_name=a.pr_name,
                    content_category=a.content_category,
                    url=a.url,
                    status=self.get_article_status(str(a.id)),
                    data_modified=a.date_modified,
                    keywords=a.keywords,
                    cover_image_url=a.cover_image_url,
                    engagement_rate=a.engagement_rate,
                    number_of_views=a.number_of_views,
                )
                for a in cluster.article_ids
            ],
            edges=self.get_edges([str(a.id) for a in cluster.article_ids]),
        )

    async def create_articles(self, articles: List[Article]) -> List[str]:
        """
        Method to create articles in the database
        :param articles: {List[ArticleMeta]}
        :return: {List[str]} List of IDs of newly created articles
        """
        article_docs = [
            ArticleDocument(
                id=a.id,
                title=a.title,
                description=a.description,
                pr_name=a.pr_name,
                content_category=a.content_category,
                url=a.url,
                date_modified=a.data_modified,
                keywords=a.keywords,
                labels=a.labels,
                cover_image_url=a.cover_image_url,
                engagement_rate=a.engagement_rate,
                number_of_views=a.number_of_views,
                content=a.content,
            )
            for a in articles
        ]
        await ArticleDocument.insert_many(article_docs)
        return [str(a.id) for a in article_docs]

    async def get_all_articles(self) -> List[ArticleMeta]:
        """
        Method to get all articles with their respective metadata.
        This will not return article contents, in order to save on memory.
        :return: {List[ArticleMeta]}
        """
        return [
            ArticleMeta(
                id=str(a.id),
                title=a.title,
                description=a.description,
                pr_name=a.pr_name,
                content_category=a.content_category,
                url=a.url,
                status=self.get_article_status(str(a.id)),
                data_modified=a.date_modified,
                keywords=a.keywords,
                cover_image_url=a.cover_image_url,
                engagement_rate=a.engagement_rate,
                number_of_views=a.number_of_views,
            )
            async for a in ArticleDocument.find_all()
        ]

    async def get_articles(self, article_ids: List[str]) -> List[ArticleMeta]:
        """
        Fetches articles with their content by specified ID.
        :param article_ids: {List[str]}
        :return: {List[Article]}
        """
        return [
            ArticleMeta(
                id=str(a.id),
                title=a.title,
                description=a.description,
                pr_name=a.pr_name,
                content_category=a.content_category,
                url=a.url,
                status=self.get_article_status(str(a.id)),
                data_modified=a.date_modified,
                keywords=a.keywords,
                cover_image_url=a.cover_image_url,
                engagement_rate=a.engagement_rate,
                number_of_views=a.number_of_views,
            )
            async for a in ArticleDocument.find_many(article_ids)
        ]

    async def create_edges(self, edges: List[Edge]) -> List[str]:
        """
        Method to create edges between articles.
        :param edges: {List[Edge]}
        :return: {List[str]} IDs of created edges
        """
        edge_docs = [
            EdgeDocument(
                start=e.start,
                end=e.end,
                weight=e.weight,
            )
            for e in edges
        ]
        await EdgeDocument.insert_many(edge_docs)
        return [str(e.id) for e in edge_docs]

    async def get_edges(self, article_ids: List[str]) -> List[Edge]:
        """
        Fetches edges between articles by specified article IDs.
        :param article_ids: {List[str]}
        :return: {List[Edge]}
        """
        edges = await EdgeDocument.find_all()
        return [
            Edge(
                start=str(e.start.id),
                end=str(e.end.id),
                weight=e.weight,
            )
            for e in edges
            if (str(e.start.id) in article_ids) and (str(e.end.id) in article_ids)
        ]

    async def create_generated_article(
        self, generated_articles: List[GeneratedArticle]
    ) -> List[str]:
        """
        Method to insert generated articles into the database
        :param generated_articles: {List[GeneratedArticle]}
        :return: {List[str]} IDs of the generated articles inserted
        """
        raise NotImplementedError()

    async def create_combine_job(
        self, cluster_id: str, sub_group_name: str, remarks: str, article_ids: List[str]
    ) -> str:
        """
        Method to create a combine job record
        :param cluster_id: {str} ID of the parent cluster
        :param sub_group_name: {str} name of the subgroup to be combined
        :param remarks: {str} remarks from the user for this sub group
        :param article_ids: {List[str]} IDs of the articles to combine
        :return: {str} id of the job just created
        """
        raise NotImplementedError()

    async def get_all_combine_jobs(self) -> List[JobCombine]:
        """
        Method to get the combine jobs that have been recorded
        :return: {List[JobCombine]}
        """
        raise NotImplementedError()

    async def create_optimise_job(
        self,
        article_id: str,
    ) -> str:
        """
        Method to mark standalone articles to be optimised as "individual" articles.
        :param article_id:
        :return:
        """
        raise NotImplementedError()

    async def get_all_optimise_jobs(self) -> List[ArticleMeta]:
        """
        Method to get all optimisation jobs recorded
        :return:{List[ArticleMeta]}
        """
        raise NotImplementedError()

    async def create_ignore_record(self, article_id: str) -> str:
        """
        Method to ignore an article based on it's own ID.
        :param article_id:
        :return:
        """
        raise NotImplementedError()
