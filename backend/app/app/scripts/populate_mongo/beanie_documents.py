from typing import List

from beanie import Document, Indexed, Link
from pydantic import Field


class ArticleDocument(Document):
    title: str
    description: str
    author: Indexed(str)
    pillar: Indexed(str)
    url: str

    status: str = Field(default="")

    labels: List[str]
    cover_image_url: str

    engagement: float
    views: int


class EdgeDocument(Document):
    start: Link[ArticleDocument]
    end: Link[ArticleDocument]
    weight: float


class ClusterDocument(Document):
    name: str
    article_ids: List[Link[ArticleDocument]] = Field(default=[])
    edges: List[Link[EdgeDocument]] = Field(default=[])
