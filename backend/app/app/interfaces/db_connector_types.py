from abc import ABC, abstractmethod
from typing import List

from app.models.article import Article
from app.models.cluster import Cluster, ClusterPopulated
from app.models.combination import Combination
from app.models.ignore import Ignore


class DbConnector(ABC):
    """
    Abstract class for interaction with databases.
    - Clusters
    - Articles
    - Combination Jobs
    - Ignore tagging
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
    async def create_clusters(self, cluster: List[Cluster]):
        pass

    @abstractmethod
    async def read_cluster_all(self) -> List[ClusterPopulated]:
        pass

    @abstractmethod
    async def read_cluster(self, cluster_id: str) -> ClusterPopulated:
        pass

    """
    Methods related to articles
    """

    @abstractmethod
    async def create_articles(self, article: List[Article]):
        pass

    @abstractmethod
    async def read_article_all(self) -> List[Article]:
        pass

    @abstractmethod
    async def read_article(self, article_id: str) -> Article:
        pass

    """
    Methods related to harmonisation jobs
    """

    @abstractmethod
    async def create_combine(self, combination: [Combination]):
        pass

    @abstractmethod
    async def read_combine_all(self) -> List[Combination]:
        pass

    @abstractmethod
    async def read_combine(self, combine_id: str) -> Combination:
        pass

    """
    Methods related to ignore tagging of articles
    """

    @abstractmethod
    async def create_ignore(self, ignore: [Ignore]):
        pass

    @abstractmethod
    async def read_ignore_all(self) -> List[Ignore]:
        pass

    @abstractmethod
    async def read_ignore(self, ignore_id: str) -> Ignore:
        pass
