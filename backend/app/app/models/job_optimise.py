from typing import Optional

from app.models.article import Article
from app.models.generated_article import GeneratedArticle
from pydantic import BaseModel


class JobOptimise(BaseModel):
    id: str
    optimise_title: bool
    title_remarks: str
    optimise_meta: bool
    meta_remarks: str
    optimise_content: bool
    content_remarks: str

    original_article: Article
    generated_article: Optional[GeneratedArticle]
