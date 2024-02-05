# define a pydantic posgresql model for article using psycopg2

from typing import Optional
from datetime import datetime as DateTime
from pydantic import BaseModel, conlist
import datetime



class Article(BaseModel):
    """Model for an article"""
    # id: Optional[int] = None
    title: Optional[str] = None
    link: Optional[str] = None
    # default to the current time
    # created_at: Optional[str] = datetime.datetime.now().isoformat()
    created_at: Optional[DateTime] = datetime.datetime.now().isoformat()
    content: Optional[str] = None

class ArticleChunk(BaseModel):
    id:int = 0
    article_id: int
    chunk: str
    chunk_id: int
    embedding: list[float] = conlist(float, min_length=1536, max_length=1536)
    created_at: DateTime

    class Config:
        orm_mode = True