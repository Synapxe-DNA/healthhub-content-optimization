"""
This file contains the Beanie document types used to interacting with the DB.
"""

from typing import List

from beanie import Document, Indexed, Link
from pydantic import Field


class ClusterDocument(Document):
    name: str
    article_ids: List[Link["ArticleDocument"]] = Field(default=[])
    edges: List["EdgeDocument"] = Field(default=[])


class ArticleDocument(Document):
    id: str

    title: str
    description: str
    author: Indexed(str)
    pillar: Indexed(str)
    url: str

    labels: List[str]
    cover_image_url: str

    engagement: float
    views: int


class EdgeDocument(Document):
    start: Link[ArticleDocument]
    end: Link[ArticleDocument]
    weight: float = Field(default=-1.0)


class HarmoniseDocument(Document):
    name: str
    article_ids: List[Link[ArticleDocument]] = Field(default=[])


class OptimiseDocument(Document):
    article_id: Link[ArticleDocument]
