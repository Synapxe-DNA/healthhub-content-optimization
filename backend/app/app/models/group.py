from typing import List

from app.models.article import ArticleMeta
from app.models.edge import Edge
from app.models.job_combine import JobCombine
from app.models.job_ignore import JobIgnore
from app.models.job_optimise import JobOptimise
from app.models.job_remove import JobRemove
from pydantic import BaseModel, Field


class Group(BaseModel):
    id: str = Field(default="")  # Will only be present when retrieving from DB

    name: str = Field(default="")
    edges: List[Edge] = Field(default=[])

    created_at: str = Field(default="")

    pending_articles: List[ArticleMeta] = Field(default=[])  # Articles not reviewed yet
    remove_articles: List[JobRemove] = Field(default=[])
    ignore_articles: List[JobIgnore] = Field(default=[])
    optimise_articles: List[JobOptimise] = Field(default=[])
    combine_articles: List[JobCombine] = Field(default=[])
