from typing import List

from app.models.job_combine import JobCombine
from app.models.job_ignore import JobIgnore
from app.models.job_optimise import JobOptimise
from app.models.job_remove import JobRemove
from pydantic import BaseModel, Field


class Job(BaseModel):
    group_id: str
    created_at: str
    remove_articles: List[JobRemove] = Field(default=[])
    ignore_articles: List[JobIgnore] = Field(default=[])
    optimise_articles: List[JobOptimise] = Field(default=[])
    combine_articles: List[JobCombine] = Field(default=[])
