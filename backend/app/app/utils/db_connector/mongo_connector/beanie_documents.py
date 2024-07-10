"""
This file contains the Beanie document types used to interacting with the DB.
"""

from typing import List, Optional

from beanie import Document, Indexed, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field


class ClusterDocument(Document):
    name: str
    article_ids: List[Link["ArticleDocument"]] = Field(default=[])
    edges: List["EdgeDocument"] = Field(default=[])


class ArticleDocument(Document):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    description: str
    pr_name: Indexed(str)
    content_category: Indexed(str)
    url: Indexed(str)

    date_modified: str

    keywords: List[str]
    cover_image_url: str

    engagement_rate: float
    number_of_views: int


class GeneratedArticleDocument(Document):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    description: str
    pr_name: Indexed(str)
    content_category: Indexed(str)
    url: Indexed(str)

    date_modified: str

    keywords: List[str]
    cover_image_url: str

    approved: bool = Field(default=False)



class EdgeDocument(Document):
    start: Link[ArticleDocument]
    end: Link[ArticleDocument]
    weight: float = Field(default=-1.0)


class JobCombineDocument(Document):
    cluster: Link[ClusterDocument]
    sub_group_name: str
    original_articles: List[Link[ArticleDocument]] = Field(default=[])
    generated_article: Optional[Link[GeneratedArticleDocument]]


class JobOptimiseDocument(Document):
    article: Link[ArticleDocument]


class IgnoreDocument(Document):
    article_id: Link[ArticleDocument]
