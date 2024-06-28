from abc import ABC, abstractmethod
from typing import List

from app.models.article import Article
from app.models.cluster import Cluster
from app.models.harmonise import Harmonise
from app.models.optimise import Optimise


class DbConnector(ABC):
    """
    Abstract class for interaction with databases.
    - Clusters
    - Articles
    - Harmonisation Jobs
    - Optimisation Jobs
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
    async def read_cluster_all(self) -> List[Cluster]:
        pass

    @abstractmethod
    async def read_cluster(self, cluster_ids: List[str]) -> List[Cluster]:
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
    async def read_article(self, article_ids: List[str]) -> List[Article]:
        pass

    """
    Methods related to harmonisation jobs
    """

    @abstractmethod
    async def create_harmonise(self, harmonisation: [Harmonise]):
        pass

    @abstractmethod
    async def read_harmonise_all(self) -> List[Harmonise]:
        pass

    @abstractmethod
    async def read_harmonise(self, harmonise_ids: List[str]) -> List[Harmonise]:
        pass

    """
    Methods related to optimisation jobs
    """

    @abstractmethod
    async def create_optimise(self, optimisation: [Optimise]):
        pass

    @abstractmethod
    async def read_optimise_all(self) -> List[Optimise]:
        pass

    @abstractmethod
    async def read_optimise(self, optimise_ids: List[str]) -> List[Optimise]:
        pass
