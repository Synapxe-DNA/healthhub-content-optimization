from pydantic import BaseModel, Field


class Optimise(BaseModel):
    id: str = Field(default='')
    article_id: str = Field()
