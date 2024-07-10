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
    author: Indexed(str)
    pillar: Indexed(str)
    url: Indexed(str)

    updated: str

    labels: List[str]
    cover_image_url: str

    engagement: float
    views: int


class EdgeDocument(Document):
    start: Link[ArticleDocument]
    end: Link[ArticleDocument]
    weight: float = Field(default=-1.0)


class CombinationDocument(Document):
    name: str
    article_ids: List[Link[ArticleDocument]] = Field(default=[])


class IgnoreDocument(Document):
    article_id: Link[ArticleDocument]
