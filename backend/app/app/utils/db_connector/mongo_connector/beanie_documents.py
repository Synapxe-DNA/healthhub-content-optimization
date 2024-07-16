"""
This file contains the Beanie document types used to interacting with the DB.
"""

from typing import List, Optional

from beanie import Document, Indexed, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


class GroupDocument(Document):
    name: str

    articles: List[Link["ArticleDocument"]]

    job: Link["JobDocument"] = None


class JobDocument(Document):
    group: Link[GroupDocument]
    created_at: str
    remove_articles: List[Link["JobRemoveDocument"]] = Field(default=[])
    ignore_articles: List[Link["JobIgnoreDocument"]] = Field(default=[])
    optimise_articles: List[Link["JobOptimiseDocument"]] = Field(default=[])
    combine_articles: List[Link["JobCombineDocument"]] = Field(default=[])


class ArticleDocument(Document):
    id: str
    title: str
    description: str
    pr_name: Indexed(str)
    content_category: Indexed(str)
    url: Indexed(str)

    date_modified: str

    keywords: List[str]
    labels: List[str]
    cover_image_url: str

    engagement_rate: float
    number_of_views: int

    content: str


class GeneratedArticleDocument(Document):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    description: str
    pr_name: Indexed(str)
    content_category: Indexed(str)
    url: Indexed(str)

    date_modified: str

    keywords: List[str]
    labels: List[str]
    cover_image_url: str

    approved: bool = Field(default=False)


class EdgeDocument(Document):
    start: Link[ArticleDocument]
    end: Link[ArticleDocument]
    weight: float = Field(default=-1.0)

    class settings:
        indexes = [
            {"fields": ["start"], "unique": False},
            {"fields": ["end"], "unique": False},
        ]


class JobCombineDocument(Document):
    group: Link[GroupDocument]
    sub_group_name: str
    remarks: str
    context: str
    original_articles: List[Link[ArticleDocument]] = Field(default=[])
    generated_article: Optional[Link[GeneratedArticleDocument]] = None


class JobOptimiseDocument(Document):
    original_article: Link[ArticleDocument]
    generated_article: Optional[Link[GeneratedArticleDocument]] = None
    optimise_title: bool
    title_remarks: str
    optimise_meta: bool
    meta_remarks: str
    optimise_content: bool
    content_remarks: str


class JobIgnoreDocument(Document):
    article: Link[ArticleDocument]
    remarks: str = Field(default="")


class JobRemoveDocument(Document):
    article: Link[ArticleDocument]
    remarks: str = Field(default="")
