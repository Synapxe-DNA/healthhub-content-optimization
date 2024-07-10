from typing import List, Optional
from pydantic import BaseModel
from app.models.article import Article


class JobOptimise(BaseModel):
    id:str
    original_article: List[Article]
    generated_article: Optional[Article]
