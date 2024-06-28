"""
This file contains the Beanie document types used to interacting with the DB.
"""
from typing import List

from beanie import Document
from bson import ObjectId
from pydantic import Field


class ClusterDocument(Document):
    name: str
    article_ids: List['str'] = Field(default=[])
    edges: List['EdgeDocument'] = Field(default=[])


class ArticleDocument(Document):
    id: str

    title: str
    description: str
    author: str
    pillar: str
    url: str

    labels: List[str]
    cover_image_url:str = Field(default='https://jollycontrarian.com/images/6/6c/Rickroll.jpg')

    engagement: float
    views: int


class EdgeDocument(Document):
    start:str
    end:str
    weight:float = Field(default=-1.0)


class HarmoniseDocument(Document):
    name: str
    article_ids: List[str] = Field(default=[])


class OptimiseDocument(Document):
    article_id: str

