from typing import List

from app.models.article import Article
from app.models.edge import Edge
from pydantic import BaseModel, Field


class Cluster(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    name: str = Field(default="")
    article_ids: List[str] = Field(default=[])
    edges: List[Edge] = Field(default=[])


class ClusterPopulated(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    name: str = Field(default="")
    articles: List[Article] = Field(default=[])
    edges: List[Edge] = Field(default=[])
