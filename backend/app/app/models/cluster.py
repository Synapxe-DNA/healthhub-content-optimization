from typing import List

from pydantic import BaseModel, Field

from app.models.article import Article
from app.models.edge import Edge


class Cluster(BaseModel):
    id: str = Field(default='')  # Will only be present when retrieving from DB

    name: str = Field(default='')
    articles: List[Article] = Field(default=[])
    edges: List[Edge] = Field(default=[])

