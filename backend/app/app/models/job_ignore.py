from app.models.article import Article
from pydantic import BaseModel


class JobIgnore(BaseModel):
    id: str
    article: Article
    remarks: str
