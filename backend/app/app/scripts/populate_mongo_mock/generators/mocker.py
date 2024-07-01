import random
from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article
from app.models.cluster import Cluster
from app.models.edge import Edge
from app.models.harmonise import Harmonise
from app.models.optimise import Optimise
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
        percent_connection: float = 0.01,
    ):
        assert num_clusters > 0, "Number of clusters must be greater than 0!"
        assert (
            min_articles_per_cluster > 0
        ), "Number of articles must be greater than 0!"
        assert (
            max_articles_per_cluster >= min_articles_per_cluster
        ), "Max must be MEQ min articles!"
        assert 1 >= percent_connection > 0, "Percent connectio must = (0,1]!"

        self.conn = db_connector
        self.num_clusters = num_clusters
        self.min_articles_per_cluster = min_articles_per_cluster
        self.max_articles_per_cluster = max_articles_per_cluster
        self.percent_connection = percent_connection

    def __create_article_ids(self) -> List[str]:
        num_articles = random.randint(
            1, (self.max_articles_per_cluster - self.min_articles_per_cluster)
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
                Edge(start=e[0], end=e[1], weight=random.uniform(0, 1))
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

            harmonise_jobs = [
                Harmonise(
                    name=random_str(16),
                    article_ids=random.sample(
                        article_ids,
                        random.randint(int(len(article_ids) / 2), len(article_ids)),
                    ),
                )
            ]

            optimise_jobs = [
                Optimise(article_id=x)
                for x in random.sample(
                    article_ids, random.randint(0, int(len(article_ids) / 2))
                )
            ]

            await self.conn.create_articles(articles)
            await self.conn.create_harmonise(harmonise_jobs)
            await self.conn.create_optimise(optimise_jobs)
            await self.conn.create_clusters([cluster])
