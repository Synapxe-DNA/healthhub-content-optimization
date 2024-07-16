from datetime import datetime
from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article, ArticleMeta
from app.models.edge import Edge
from app.models.generated_article import GeneratedArticle
from app.models.group import Group
from app.models.job import Job
from app.models.job_combine import JobCombine
from app.models.job_ignore import JobIgnore
from app.models.job_optimise import JobOptimise
from app.models.job_remove import JobRemove
from app.utils.db_connector.mongo_connector.beanie_documents import (
    ArticleDocument,
    EdgeDocument,
    GeneratedArticleDocument,
    GroupDocument,
    JobCombineDocument,
    JobDocument,
    JobIgnoreDocument,
    JobOptimiseDocument,
    JobRemoveDocument,
)
from beanie import exceptions, init_beanie
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
                GroupDocument,
                ArticleDocument,
                GeneratedArticleDocument,
                EdgeDocument,
                JobDocument,
                JobCombineDocument,
                JobOptimiseDocument,
                JobIgnoreDocument,
                JobRemoveDocument,
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

    @staticmethod
    async def __convertToJob(jobDoc: JobDocument) -> Job:
        return Job(
            group=jobDoc.group,
            created_at=jobDoc.created_at,
            remove_articles=jobDoc.remove_articles,
            optimise_articles=jobDoc.optimise_articles,
            ignore_articles=jobDoc.ignore_articles,
            combine_articles=jobDoc.combine_articles,
        )

    async def __convertToGroup(self, groupDoc: GroupDocument) -> Group:
        return Group(
            id=str(groupDoc.id),
            name=groupDoc.name,
            articles=[self.__convertToArticleMeta(a) for a in groupDoc.article_ids],
            edges=self.get_edges([str(a.id) for a in groupDoc.article_ids]),
            job=self.__convertToJob(groupDoc.job),
        )

    # endregion

    """
    Class methods to interact with DB
    """

    # region Methods related to groups

    async def create_group_from_articles(
        self, group_name: str, article_ids: List[str]
    ) -> str:
        """
        Method to group a group from existing articles
        :param group_name: {str} Name of group
        :param article_ids: {List[str]} List of IDs of articles
        :return: {str} ID of newly created group
        """
        group = GroupDocument(name=group_name, articles=article_ids)
        await group.insert()
        return str(group.id)

    async def get_all_groups(self) -> List[Group]:
        """
        Method to retrieve all groups, populated with their respective ArticleMeta and Edges
        :return: {List[Group]}
        """

        return [
            self.__convertToGroup(c)
            async for c in GroupDocument.find_all(fetch_links=True)
        ]

    async def get_group(self, group_id: str) -> Group:
        """
        Method to fetch a group by ID.
        :param group_id:
        :return:
        """
        group = await GroupDocument.get(group_id)

        return self.__convertToGroup(group)

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

    # region Methods related to jobs

    async def create_job(
        self,
        group_id: str,
        remove_jobs: List[str],
        optimise_jobs: List[str],
        ignore_jobs: List[str],
        combine_jobs: List[str],
    ) -> str:
        """
        Method to create a job record
        :param remove_jobs: {List[JobRemove]}
        :param optimise_jobs: {List[JobOptimise]}
        :param ignore_jobs: {List[JobIgnore]}
        :param combine_jobs: {List[JobCombine]}
        :return: {str} id of the job just created
        """

        job = JobDocument(
            created_at=str(datetime.now()),
            group=await GroupDocument.get(ObjectId(group_id)),
            remove_articles=[
                await JobRemoveDocument.get(ObjectId(r)) for r in remove_jobs
            ],
            optimise_articles=[
                await JobOptimiseDocument.get(ObjectId(o)) for o in optimise_jobs
            ],
            ignore_articles=[
                await JobIgnoreDocument.get(ObjectId(i)) for i in ignore_jobs
            ],
            combine_articles=[
                await JobCombineDocument.get(ObjectId(c)) for c in combine_jobs
            ],
        )

        await JobDocument.insert(job)

        group = await GroupDocument.get(group_id)
        group.job = job
        try:
            await group.replace()
        except (ValueError, exceptions.DocumentNotFound):
            print("Can't replace a non existing document")

        return job.id

    async def get_job(self, job_id: str) -> Job:
        job = await JobDocument.get(job_id)
        return Job(
            group_id=job.group.id,
            created_at=job.created_at,
            remove_articles=[self.get_remove_job(r.id) for r in job.remove_articles],
            optimise_articles=[
                self.get_optimise_job(o.id) for o in job.optimise_articles
            ],
            ignore_articles=[self.get_ignore_job(i.id) for i in job.ignore_articles],
            combine_articles=[self.get_combine_job(c.id) for c in job.combine_articles],
        )

    # endregion

    # region Methods related to combination jobs

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
        combine_job = JobCombineDocument(
            group=group_id,
            sub_group_name=sub_group_name,
            remarks=remarks,
            context=context,
            original_articles=article_ids,
        )

        await JobCombineDocument.insert(combine_job)

        return str(combine_job.id)

    async def get_combine_job(self, job_combine_id) -> JobCombine:
        """
        Method to get a combine job record
        :param job_combine_id: {str} ID of the combine job
        :return: {JobCombine} combine job record
        """
        job_combine = JobCombineDocument.get(job_combine_id)
        return JobCombine(
            group_id=job_combine.group.id,
            group_name=job_combine.group.name,
            sub_group_name=job_combine.sub_group_name,
            remarks=job_combine.remarks,
            context=job_combine.context,
            original_articles=[
                self.__convertToArticle(a) for a in job_combine.original_articles
            ],
            generated_article=job_combine.generated_article,
        )

    async def get_all_combine_jobs(self) -> List[JobCombine]:
        """
        Method to get the combine jobs that have been recorded
        :return: {List[JobCombine]}
        """
        return [
            JobCombine(
                id=str(j.id),
                group_id=str(j.group.id),
                group_name=j.group.name,
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
        optimise_article = JobOptimiseDocument(
            original_article=article_id,
            optimise_title=optimise_title,
            optimise_meta=optimise_meta,
            optimise_content=optimise_content,
            title_remarks=title_remarks,
            meta_remarks=meta_remarks,
            content_remarks=content_remarks,
        )
        await JobOptimiseDocument.insert(optimise_article)

        return str(optimise_article.id)

    async def get_optimise_job(self, job_optimise_id):
        """
        Method to get a optimise job record
        :param job_optimise_id: {str} ID of the optimise job
        :return: {JobOptimise} optimise job record
        """
        job_optimise = JobOptimiseDocument.get(job_optimise_id)
        return JobOptimise(
            original_article=self.__convertToArticle(job_optimise.original_article),
            optimise_title=job_optimise.optimise_title,
            optimise_meta=job_optimise.optimise_meta,
            optimise_content=job_optimise.optimise_content,
            title_remarks=job_optimise.title_remarks,
            meta_remarks=job_optimise.meta_remarks,
            content_remarks=job_optimise.content_remarks,
        )

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

    async def create_ignore_job(self, article_id: str) -> str:
        """
        Method to ignore an article based on it's own ID.
        :param article_id:
        :return: {str} id of article ignored
        """
        ignore_doc = JobIgnoreDocument(article=article_id)
        await JobIgnoreDocument.insert(ignore_doc)
        return str(ignore_doc.id)

    async def get_ignore_job(self, job_ignore_id):
        """
        Method to get a ignore job record
        :param job_ignore_id: {str} ID of the ignore job
        :return: {JobIgnore} ignore job record
        """
        job_ignore = JobIgnoreDocument.get(job_ignore_id)
        return JobIgnore(
            article=self.__convertToArticle(job_ignore.article),
            remarks=job_ignore.remarks,
        )

    async def get_all_ignore_jobs(self) -> List[ArticleMeta]:
        return [
            self.__convertToArticleMeta(a.article)
            async for a in JobRemoveDocument.find_all()
        ]

    # endregion

    # region Methods related to removed articles

    async def create_remove_job(self, article_id: str, remarks: str) -> str:
        """
        Method to remove an article based on it's own ID.
        :param article_id:
        :param remarks:
        :return: {str} id of article removed
        """
        remove_doc = JobRemoveDocument(article=article_id, remarks=remarks)
        await JobRemoveDocument.insert(remove_doc)
        return str(remove_doc.id)

    async def get_remove_job(self, job_remove_id):
        """
        Method to get a remove job record
        :param job_remove_id: {str} ID of the remove job
        :return: {JobRemove} remove job record
        """
        job_remove = JobRemoveDocument.get(job_remove_id)
        return JobRemove(
            article=self.__convertToArticle(job_remove.article),
            remarks=job_remove.remarks,
        )

    async def get_all_remove_jobs(self) -> List[ArticleMeta]:
        return [
            self.__convertToArticleMeta(a.article)
            async for a in JobRemoveDocument.find_all()
        ]

    # endregion
