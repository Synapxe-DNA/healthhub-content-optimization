from abc import ABC, abstractmethod
from typing import List

from app.models.article import Article, ArticleMeta
from app.models.cluster import Cluster
from app.models.edge import Edge
from app.models.generated_article import GeneratedArticle
from app.models.job_combine import JobCombine


class DbConnector(ABC):
    """
    Abstract class for a query engine abstraction.
    This ABC contains methods that execute and parse database queries, tailored for specific data manipulation needs.
    """

    """
    Method to instantiate connection and complete setup
    """

    @abstractmethod
    async def connect(self) -> None:
        pass

    """
    Methods related to clusters
    """

    @abstractmethod
    async def create_cluster_from_articles(
        self, cluster_name: str, article_ids: List[str]
    ) -> str:
        """
        Method to group a cluster from existing articles
        :param cluster_name: {str} Name of cluster
        :param article_ids: {List[str]} List of IDs of articles
        :return: {str} ID of newly created cluster
        """
        pass

    @abstractmethod
    async def get_all_clusters(self) -> List[Cluster]:
        """
        Method to retrieve all clusters, populated with their respective ArticleMeta and Edges
        :return: {List[Cluster]}
        """
        pass

    @abstractmethod
    async def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Method to fetch a cluster by ID.
        :param cluster_id:
        :return:
        """
        pass

    """
    Methods related to articles
    """

    @abstractmethod
    async def create_articles(self, articles: List[Article]) -> List[str]:
        pass

    @abstractmethod
    async def get_all_articles(self) -> List[ArticleMeta]:
        """
        Method to get all articles with their respective metadata.
        This will not return article contents, in order to save on memory.
        :return: {List[ArticleMeta]}
        """
        pass

    @abstractmethod
    async def get_articles(self, article_ids: List[str]) -> List[Article]:
        """
        Fetches articles with their content by specified ID.
        :param article_ids: {List[str]}
        :return: {List[Article]}
        """
        pass

    """
    Methods related to article edges
    """

    @abstractmethod
    async def create_edges(self, edges: List[Edge]) -> List[str]:
        """
        Method to create edges between articles.
        :param edges: {List[Edge]}
        :return: {List[str]} IDs of created edges
        """
        pass

    @abstractmethod
    async def get_edges(self, article_ids: List[str]) -> List[Edge]:
        """
        Fetches edges between articles by specified IDs.
        :param article_ids: {List[str]}
        :return: {List[Edge]}
        """
        pass

    """
    Methods related to generated articles
    """

    @abstractmethod
    async def create_generated_article(
        self, generated_articles: List[GeneratedArticle]
    ) -> List[str]:
        """
        Method to insert generated articles into the database
        :param generated_articles: {List[GeneratedArticle]}
        :return: {List[str]} IDs of the generated articles inserted
        """
        pass

    """
    Methods related to combination jobs
    """

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_all_combine_jobs(self) -> List[JobCombine]:
        """
        Method to get the combine jobs that have been recorded
        :return: {List[JobCombine]}
        """
        pass

    """
    Methods related to standalone articles to optimise
    """

    @abstractmethod
    async def create_optimise_job(
        self,
        article_id: str,
    ) -> str:
        """
        Method to mark standalone articles to be optimised as "individual" articles.
        :param article_id:
        :return:
        """
        pass

    @abstractmethod
    async def get_all_optimise_jobs(self) -> List[ArticleMeta]:
        """
        Method to get all optimisation jobs recorded
        :return:{List[ArticleMeta]}
        """
        pass

    """
    Methods related to ignored articles
    """

    @abstractmethod
    async def create_ignore_record(self, article_id: str) -> str:
        """
        Method to ignore an article based on it's own ID.
        :param article_id:
        :return:
        """
        pass
