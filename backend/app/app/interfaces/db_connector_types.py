from abc import ABC, abstractmethod
from typing import List

from app.models.article import Article, ArticleMeta
from app.models.cluster import Cluster
from app.models.edge import Edge


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
    Methods related to generated articles
    TODO will commit soon
    """
