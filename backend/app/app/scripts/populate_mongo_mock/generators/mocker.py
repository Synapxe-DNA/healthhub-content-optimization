import random
from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.combination import Combination
from app.models.edge import Edge
from app.models.ignore import Ignore
from app.scripts.populate_mongo_mock.generators.string_generator import (
    random_id,
    random_str,
)


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
        return [random_id(32) for _ in range(num_articles)]

    async def mock(self) -> None:

        await self.conn.connect()

        authors = [random_str(random.randint(5, 20)).strip() for _ in range(5)]
        labels = [random_str(random.randint(5, 10)).strip() for _ in range(10)]
        pillar = [random_str(random.randint(3, 10)).strip() for _ in range(10)]

        for i in range(self.num_clusters):

            print(f"Mocking cluster {i+1}")

            article_ids = self.__create_article_ids()

            articles = [
                Article(
                    id=x,
                    title=random_str(),
                    description=random_str(128),
                    author=random.choice(authors),
                    pillar=random.choice(pillar),
                    labels=random.sample(
                        labels, random.randint(0, int(len(labels) / 2))
                    ),
                    url="url",
                    cover_image_url="image_url",
                    engagement=random.uniform(0, 1),
                    views=random.randint(100, 99999),
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

            cluster = Cluster(
                name=f"Cluster {random_str(5)}", article_ids=article_ids, edges=edges
            )

            combine_ids = []
            ignore_ids = []

            if(bool(random.getrandbits(1))):
                for id in article_ids:
                    if(bool(random.getrandbits(1))):
                        combine_ids.append(id)
                    else:
                        ignore_ids.append(id)
  
            

            combine_jobs = [
                Combination(
                    name=random_str(16),
                    article_ids=combine_ids,
                )
            ]


            ### Removed mocking of ignore jobs to keep mocking process simple.
            ### This can be manually tested on the frontend.
            ignore_jobs = [
                Ignore(article_id=x)
                for x in ignore_ids
            ]

            await self.conn.create_articles(articles)
            await self.conn.create_clusters([cluster])

            # if random.uniform(0, 1) > self.percent_processed:
            await self.conn.create_combine(combine_jobs)
            await self.conn.create_ignore(ignore_jobs)
