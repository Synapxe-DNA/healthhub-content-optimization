from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article, ArticleMeta
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

    # region Client Setup

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
                RemoveDocument,
            ],
        )

    # endregion

    # region Helper functions

    @staticmethod
    async def __convertToArticleMeta(articleDoc: ArticleDocument) -> ArticleMeta:
        return ArticleMeta(
            id=articleDoc.id,
            title=articleDoc.title,
            description=articleDoc.description,
            pr_name=articleDoc.pr_name,
            content_category=articleDoc.content_category,
            url=articleDoc.url,
            date_modified=articleDoc.date_modified,
            keywords=articleDoc.keywords,
            labels=articleDoc.labels,
            cover_image_url=articleDoc.cover_image_url,
            engagement_rate=articleDoc.engagement_rate,
            number_of_views=articleDoc.number_of_views,
        )

    @staticmethod
    async def __convertToArticle(articleDoc: ArticleDocument) -> Article:
        return ArticleMeta(
            id=articleDoc.id,
            title=articleDoc.title,
            description=articleDoc.description,
            pr_name=articleDoc.pr_name,
            content_category=articleDoc.content_category,
            url=articleDoc.url,
            date_modified=articleDoc.date_modified,
            keywords=articleDoc.keywords,
            labels=articleDoc.labels,
            cover_image_url=articleDoc.cover_image_url,
            engagement_rate=articleDoc.engagement_rate,
            number_of_views=articleDoc.number_of_views,
            content=articleDoc.content,
        )

    async def __convertToCluster(self, clusterDoc: ClusterDocument) -> Cluster:
        return Cluster(
            id=str(clusterDoc.id),
            name=clusterDoc.name,
            articles=[self.__convertToArticleMeta(a) for a in clusterDoc.article_ids],
            edges=self.get_edges([str(a.id) for a in clusterDoc.article_ids]),
        )

    # endregion

    """
    Class methods to interact with DB
    """

    # region Methods related to clusters

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
            self.__convertToCluster(c)
            async for c in ClusterDocument.find_all(fetch_links=True)
        ]

    async def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Method to fetch a cluster by ID.
        :param cluster_id:
        :return:
        """
        cluster = await ClusterDocument.get(cluster_id)

        return self.__convertToCluster(cluster)

    # endregion

    # region Methods related to articles

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
                date_modified=a.date_modified,
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
            self.__convertToArticleMeta(a) async for a in ArticleDocument.find_all()
        ]

    async def get_articles(self, article_ids: List[str]) -> List[ArticleMeta]:
        """
        Fetches articles with their content by specified ID.
        :param article_ids: {List[str]}
        :return: {List[Article]}
        """
        return [
            self.__convertToArticleMeta(a)
            async for a in ArticleDocument.find_many(article_ids)
        ]

    # endregion

    # region Methods related to article edges

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

    # endregion

    # region Methods related to generated articles

    async def create_generated_article(
        self, generated_articles: List[GeneratedArticle]
    ) -> List[str]:
        """
        Method to insert generated articles into the database
        :param generated_articles: {List[GeneratedArticle]}
        :return: {List[str]} IDs of the generated articles inserted
        """
        raise NotImplementedError()

    # endregion

    # region Methods related to combination jobs

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
        combine_job = JobCombineDocument(
            cluster=cluster_id,
            sub_group_name=sub_group_name,
            remarks=remarks,
            original_articles=article_ids,
        )

        await JobCombineDocument.insert(combine_job)

        return str(combine_job.id)

    async def get_all_combine_jobs(self) -> List[JobCombine]:
        """
        Method to get the combine jobs that have been recorded
        :return: {List[JobCombine]}
        """
        return [
            JobCombine(
                id=str(j.id),
                group_id=str(j.cluster.id),
                group_name=j.cluster.name,
                sub_group_name=j.sub_group_name,
                remarks=j.remarks,
                original_articles=[
                    self.__convertToArticle(a) for a in j.original_articles
                ],
            )
            for j in JobCombineDocument.find_all()
        ]

    # endregion

    # region Methods related to standalone articles to optimise

    async def create_optimise_job(self, article_id: str) -> str:
        """
        Method to mark standalone articles to be optimised as "individual" articles.
        :param article_id:
        :return: {str} id of the job just created
        """
        optimise_article = JobOptimiseDocument(original_article=article_id)
        await JobOptimiseDocument.insert(optimise_article)

        return str(optimise_article.id)

    async def get_all_optimise_jobs(self) -> List[ArticleMeta]:
        """
        Method to get all optimisation jobs recorded
        :return:{List[ArticleMeta]}
        """

        return [
            self.__convertToArticleMeta(a.original_article)
            async for a in JobOptimiseDocument.find_all()
        ]

    # endregion

    # region Methods related to ignored articles

    async def create_ignore_record(self, article_id: str) -> str:
        """
        Method to ignore an article based on it's own ID.
        :param article_id:
        :return: {str} id of article ignored
        """
        ignore_doc = IgnoreDocument(article=article_id)
        await IgnoreDocument.insert(ignore_doc)
        return str(ignore_doc.id)

    # endregion

    # region Methods related to removed articles

    async def create_remove_record(self, article_id: str, remarks: str) -> str:
        """
        Method to remove an article based on it's own ID.
        :param article_id:
        :param remarks:
        :return: {str} id of article removed
        """
        remove_doc = RemoveDocument(article=article_id, remarks=remarks)
        await RemoveDocument.insert(remove_doc)
        return str(remove_doc.id)

    # endregion
