from abc import ABC, abstractmethod
from typing import List

from app.models.article import Article, ArticleMeta
from app.models.edge import Edge
from app.models.generated_article import GeneratedArticle
from app.models.group import Group
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
    Methods related to groups
    """

    @abstractmethod
    async def create_group_from_articles(
        self, group_name: str, article_ids: List[str]
    ) -> str:
        """
        Method to group a group from existing articles
        :param group_name: {str} Name of group
        :param article_ids: {List[str]} List of IDs of articles
        :return: {str} ID of newly created group
        """
        pass

    @abstractmethod
    async def get_all_groups(self) -> List[Group]:
        """
        Method to retrieve all groups, populated with their respective ArticleMeta and Edges
        :return: {List[Group]}
        """
        pass

    @abstractmethod
    async def get_group(self, group_id: str) -> Group:
        """
        Method to fetch a group by ID.
        :param group_id:
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
        self,
        group_id: str,
        sub_group_name: str,
        article_ids: List[str],
        remarks: str = "",
        context: str = "",
    ) -> str:
        """
        Method to create a combine job record
        :param group_id: {str} ID of the parent group
        :param sub_group_name: {str} name of the subgroup to be combined
        :param article_ids: {List[str]} IDs of the articles to combine
        :param remarks: {str} remarks from the user for this sub group
        :param context: {str} context from user to add on to this subgroup
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
        optimise_title: bool,
        optimise_meta: bool,
        optimise_content: bool,
        title_remarks: str = "",
        meta_remarks: str = "",
        content_remarks: str = "",
    ) -> str:
        """
        Method to mark standalone articles to be optimised as "individual" articles.
        :param article_id:
        :param optimise_title: True if title needs to be optimised
        :param optimise_meta: True if meta needs to be optimised
        :param optimise_content: True if content needs to be optimised
        :param title_remarks: Optional remarks for title optimisation
        :param meta_remarks: Optional remarks for meta optimisation
        :param content_remarks: Optional remarks for content optimisation
        :return: {str} id of the job just created
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
    async def create_ignore_job(self, article_id: str) -> str:
        """
        Method to ignore an article based on it's own ID.
        :param article_id:
        :return: {str} id of article ignored
        """
        pass

    @abstractmethod
    async def get_all_ignore_jobs(self) -> List[ArticleMeta]:
        """
        Method to get all remove records
        :return: {List[JobCombine]}
        """
        pass

    """
    Methods related to removed articles
    """

    @abstractmethod
    async def create_remove_job(self, article_id: str, remarks: str) -> str:
        """
        Method to remove an article based on it's own ID.
        :param article_id:
        :param remarks:
        :return: {str} id of article removed
        """
        pass

    @abstractmethod
    async def get_all_remove_jobs(self) -> List[ArticleMeta]:
        """
        Method to get all remove records
        :return: {List[JobCombine]}
        """
        pass
