import asyncio
import datetime
import random
from typing import List

from app.interfaces.db_connector_types import DbConnector
from app.models.article import Article, ArticleStatus
from app.models.edge import Edge
from app.scripts.populate_mongo_mock.generators.string_generator import random_str
from bson import ObjectId


class Mocker:

    def __init__(
        self,
        db_connector: DbConnector,
        num_groups: int = 10,
        min_articles_per_group: int = 25,
        max_articles_per_group: int = 100,
        percent_connection: float = 0.01,
    ):
        """
        Create a new mocker object
        :param db_connector: {DbConnector} object for connecting to DB
        :param num_groups: Number of groups to mock
        :param min_articles_per_group: Minimum number of articles per group
        :param max_articles_per_group: Maximum number of articles per group
        :param percent_connection: Proportion of articles within a groups with edges
        """

        assert num_groups > 0, "Number of groups must be greater than 0!"
        assert min_articles_per_group > 0, "Number of articles must be greater than 0!"
        assert (
            max_articles_per_group >= min_articles_per_group
        ), "Max must be MEQ min articles!"
        assert 1 >= percent_connection > 0, "Percent connection must = (0,1]!"

        self.conn = db_connector
        self.num_groups = num_groups
        self.min_articles_per_group = min_articles_per_group
        self.max_articles_per_group = max_articles_per_group
        self.percent_connection = percent_connection

        self.pr_name = [random_str(random.randint(5, 20)).strip() for _ in range(5)]
        self.labels = [random_str(random.randint(5, 10)).strip() for _ in range(10)]
        self.keywords = [random_str(random.randint(5, 10)).strip() for _ in range(10)]
        self.content_category = [
            random_str(random.randint(3, 10)).strip() for _ in range(10)
        ]

    def __create_article_ids(self) -> List[str]:
        num_articles = random.randint(
            1, (self.max_articles_per_group - self.min_articles_per_group)
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
    Method to generate the status of an article based on the number of articles in a group

    If group size is greater than 1, the article status can either be Combined, Removed, Ignored or Optimised.
    However, in a group of size greater than 1, there must be at least 2 articles with the status of Combined.

    Else if group size is 1, the article status can be any of the 3 statuses except Combined.
    """

    def __generate_article_status(self, group_size: int) -> List[str]:

        if group_size > 1:
            statuses = [status.value for status in ArticleStatus]
            statuses_list = [ArticleStatus.COMBINE.value for i in range(2)]

            remaining_statuses = random.choices(statuses, k=group_size - 2)

            statuses_list.extend(remaining_statuses)
            random.shuffle(statuses_list)

            return statuses_list
        else:
            statuses = [status.value for status in ArticleStatus]
            statuses.remove(ArticleStatus.COMBINE.value)

            return [random.choice(statuses)]

    async def __create_combine_articles(
        self, group_id: str, combine_ids: List[str]
    ) -> None:
        subgroup_num = 1

        while len(combine_ids) > 1:
            if (len(combine_ids) - 2) < 2:
                group_size = len(combine_ids)
            else:
                group_size = random.randint(
                    2, len(combine_ids) - 2
                )  # Create subgroups of varying sizes, minimum 2

            combine_job = await self.conn.create_combine_job(
                group_id,
                f"Subgroup {subgroup_num}",
                combine_ids[:group_size],
            )

            self.combine_jobs.append(combine_job)

            subgroup_num += 1
            combine_ids = combine_ids[group_size:]

    def __create_article(self, article_id: str, status: str) -> Article:

        return Article(
            id=article_id,
            title=random_str(),
            description=random_str(128),
            pr_name=random.choice(self.pr_name),
            content_category=random.choice(self.content_category),
            url="url",
            status=status,
            date_modified=self._create_date(),
            keywords=random.sample(
                self.keywords, random.randint(0, int(len(self.keywords) / 2))
            ),
            labels=random.sample(
                self.labels, random.randint(0, int(len(self.labels) / 2))
            ),
            cover_image_url="image_url",
            engagement_rate=random.uniform(0, 1),
            number_of_views=random.randint(100, 99999),
            content=random_str(128),
        )

    def __create_edges(self, article_ids: List[str]) -> List[Edge]:
        return [
            Edge(start=e[0], end=e[1], weight=random.uniform(0.5, 1))
            for e in [
                random.sample(article_ids, 2)
                for _ in range(int(self.percent_connection * (len(article_ids) ** 2)))
            ]
        ]

    async def create_articles(self, article_ids: List[str]) -> List[Article]:
        articles = []
        self.remove_ids = []
        self.ignore_ids = []
        self.optimise_ids = []
        self.combine_ids = []

        self.combine_jobs = []
        self.reviewed = bool(random.getrandbits(1))

        if self.reviewed:  # Randomly decide if group has been reviewed
            article_statuses = self.__generate_article_status(len(article_ids))

            for x in article_ids:
                article_status = article_statuses.pop()

                if article_status == ArticleStatus.REMOVE.value:
                    self.remove_ids.append(x)
                elif article_status == ArticleStatus.IGNORE.value:
                    self.ignore_ids.append(x)
                elif article_status == ArticleStatus.OPTIMISE.value:
                    self.optimise_ids.append(x)
                elif article_status == ArticleStatus.COMBINE.value:
                    self.combine_ids.append(x)

                articles.append(self.__create_article(x, article_status))

        else:
            for x in article_ids:
                articles.append(self.__create_article(x, ""))

        return articles

    async def mock(self) -> None:

        await self.conn.connect()

        for i in range(self.num_groups):

            print(f"Mocking group {i+1}")

            group_name = f"Group {random_str(5)}"

            article_ids = self.__create_article_ids()

            articles = await self.create_articles(article_ids)

            edges = self.__create_edges(article_ids) if len(article_ids) > 1 else []

            await self.conn.create_articles(articles)
            group_id = await self.conn.create_group_from_articles(
                group_name, article_ids
            )
            if len(edges) > 0:
                await self.conn.create_edges(edges)

            if self.reviewed:
                if len(self.combine_ids) > 0:
                    await self.__create_combine_articles(group_id, self.combine_ids)

                ignore_jobs = await asyncio.gather(
                    *(self.conn.create_ignore_job(i) for i in self.ignore_ids)
                )
                remove_jobs = await asyncio.gather(
                    *(
                        self.conn.create_remove_job(r, random_str())
                        for r in self.remove_ids
                    )
                )

                optimise_jobs = await asyncio.gather(
                    *(
                        self.conn.create_optimise_job(
                            o,
                            bool(random.getrandbits(1)),
                            bool(random.getrandbits(1)),
                            bool(random.getrandbits(1)),
                        )
                        for o in self.optimise_ids
                    )
                )

                await self.conn.create_job(
                    group_id=group_id,
                    remove_jobs=remove_jobs,
                    optimise_jobs=optimise_jobs,
                    ignore_jobs=ignore_jobs,
                    combine_jobs=self.combine_jobs,
                )
