from enum import Enum
from typing import List

from app.utils.db_connector.mongo_connector.beanie_documents import ArticleDocument
from pydantic import BaseModel, Field


class ArticleMeta(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    title: str = Field()
    description: str = Field()
    pr_name: str = Field()
    content_category: str = Field()
    url: str = Field(default="")

    status: str = Field(default="")

    date_modified: str = Field(default="")

    # Article peripheral information
    keywords: List[str] = Field(default=[])
    labels: List[str] = Field(default=[])
    cover_image_url: str = Field(default="")

    # Article statistics
    engagement_rate: float = Field(default=-1.0)
    number_of_views: int = Field(default=-1)

    @classmethod
    def convert(cls, articleDoc: ArticleDocument):
        return cls(
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


class Article(ArticleMeta):
    content: str

    @classmethod
    def convert(cls, articleDoc: ArticleDocument):
        return cls(
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


class ArticleStatus(Enum):
    COMBINE = "Combined"
    IGNORE = "Ignored"
    OPTIMISE = "Optimise"
    REMOVE = "Remove"
