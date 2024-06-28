from pydantic import BaseModel, Field


class Edge(BaseModel):
    start:str = Field()
    end:str = Field()
    weight:float = Field(default=-1.0)
