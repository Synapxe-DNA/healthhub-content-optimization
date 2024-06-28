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
    Methods related to clusters
    """

    @abstractmethod
    def create_clusters(self, cluster:List[Cluster]):
        pass

    @abstractmethod
    def read_cluster_all(self) -> List[Cluster]:
        pass

    @abstractmethod
    def read_cluster(self, cluster_ids:List[str]) -> List[Cluster]:
        pass


    """
    Methods related to articles
    """

    @abstractmethod
    def create_article(self, article:List[Article]):
        pass

    @abstractmethod
    def read_article_all(self) -> List[Article]:
        pass

    @abstractmethod
    def read_article(self, article_ids:List[str]) -> List[Article]:
        pass


    """
    Methods related to harmonisation jobs
    """

    @abstractmethod
    def create_harmonise(self, harmonisation:Harmonise):
        pass

    @abstractmethod
    def read_harmonise_all(self) -> List[Harmonise]:
        pass

    @abstractmethod
    def read_harmonise(self, harmonise_ids:List[str]) -> List[Harmonise]:
        pass


    """
    Methods related to optimisation jobs
    """

    @abstractmethod
    def create_optimise(self, harmonisation:Optimise):
        pass

    @abstractmethod
    def read_optimise_all(self) -> List[Optimise]:
        pass

    @abstractmethod
    def read_optimise(self, harmonise_ids:List[str]) -> List[Optimise]:
        pass

