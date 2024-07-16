from typing import List

from app.models.article import ArticleMeta
from app.models.edge import Edge
from app.models.job import Job
from pydantic import BaseModel, Field


class Group(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    name: str = Field(default="")
    edges: List[Edge] = Field(default=[])

    articles: List[ArticleMeta] = Field(default=[])  # Articles not reviewed yet
    job: Job = Field(default=None)
