from app.models.article import Article
from pydantic import BaseModel


class JobIgnore(BaseModel):
    article: Article
    remarks: str
