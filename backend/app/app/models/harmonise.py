from typing import List

from pydantic import BaseModel, Field


class Harmonise(BaseModel):
    id: str = Field(default='')  # Will only be present when retrieving from DB
    name: str = Field()
    article_ids: List[str] = Field(default=[])
