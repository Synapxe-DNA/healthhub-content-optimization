import datetime
import random
from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.edge import Edge
from app.scripts.populate_mongo_mock.generators.string_generator import random_str
from bson import ObjectId


class Mocker:

    def __init__(
        self,
        db_connector: DbConnector,
        num_clusters: int = 10,
        min_articles_per_cluster: int = 25,
        max_articles_per_cluster: int = 100,
        percent_processed: float = 0.5,
        percent_connection: float = 0.01,
    ):
        """
        Create a new mocker object
        :param db_connector: {DbConnector} object for connecting to DB
        :param num_clusters: Number of clusters to mock
        :param min_articles_per_cluster: Minimum number of articles per cluster
        :param max_articles_per_cluster: Maximum number of articles per cluster
        :param percent_processed: Proportion of clusters that relate to "combination" jobs
        :param percent_connection: Proportion of articles within a cluster with edges
        """

        assert num_clusters > 0, "Number of clusters must be greater than 0!"
        assert (
            min_articles_per_cluster > 0
        ), "Number of articles must be greater than 0!"
        assert (
            max_articles_per_cluster >= min_articles_per_cluster
        ), "Max must be MEQ min articles!"
        assert 1 >= percent_processed >= 0, "Percent processed must = [0,1]!"
        assert 1 >= percent_connection > 0, "Percent connection must = (0,1]!"

        self.conn = db_connector
        self.num_clusters = num_clusters
        self.min_articles_per_cluster = min_articles_per_cluster
        self.max_articles_per_cluster = max_articles_per_cluster
        self.percent_processed = percent_processed
        self.percent_connection = percent_connection

    def __create_article_ids(self) -> List[str]:
        num_articles = random.randint(
            2, (self.max_articles_per_cluster - self.min_articles_per_cluster)
        )
        # return [random_id(32) for _ in range(num_articles)]
        return [str(ObjectId()) for _ in range(num_articles)]

    def _create_date(self) -> str:
        start_dt = datetime.date(2024, 5, 13)
        end_dt = datetime.date(2024, 10, 25)
        time_between_dates = end_dt - start_dt
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_dt + datetime.timedelta(days=random_number_of_days)
        return str(random_date)

    """
    Method to generate the status of an article based on the number of articles in a cluster

    If cluster size is greater than 1, the status is "Combined" as the articles should be cominbed
    else the status is "Ignored" as default.
    """

    async def mock(self) -> None:

        await self.conn.connect()

        authors = [random_str(random.randint(5, 20)).strip() for _ in range(5)]
        labels = [random_str(random.randint(5, 10)).strip() for _ in range(10)]
        keywords = [random_str(random.randint(5, 10)).strip() for _ in range(10)]
        pillar = [random_str(random.randint(3, 10)).strip() for _ in range(10)]

        for i in range(self.num_clusters):

            print(f"Mocking cluster {i+1}")

            article_ids = self.__create_article_ids()

            articles = [
                Article(
                    id=x,
                    title=random_str(),
                    description=random_str(128),
                    pr_name=random.choice(authors),
                    content_category=random.choice(pillar),
                    url="url",
                    status="status",
                    date_modified=self._create_date(),
                    keywords=random.sample(
                        keywords, random.randint(0, int(len(keywords) / 2))
                    ),
                    labels=random.sample(
                        labels, random.randint(0, int(len(labels) / 2))
                    ),
                    cover_image_url="image_url",
                    engagement_rate=random.uniform(0, 1),
                    number_of_views=random.randint(100, 99999),
                    content=random_str(128),
                )
                for x in article_ids
            ]

            edges = [
                Edge(start=e[0], end=e[1], weight=random.uniform(0.5, 1))
                for e in [
                    random.sample(article_ids, 2)
                    for _ in range(
                        int(self.percent_connection * (len(article_ids) ** 2))
                    )
                ]
            ]

            await self.conn.create_articles(articles)
            await self.conn.create_cluster_from_articles(
                "Cluster {random_str(5)}", article_ids
            )
            if len(edges) > 0:
                await self.conn.create_edges(edges)
