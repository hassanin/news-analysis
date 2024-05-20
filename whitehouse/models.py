# define a pydantic posgresql model for article using psycopg2

from typing import Optional
from datetime import datetime as DateTime
from pydantic import BaseModel, conlist
import datetime


class Article(BaseModel):
    """Model for an article"""

    id: Optional[int] = None
    title: Optional[str] = None
    link: Optional[str] = None
    # default to the current time
    # created_at: Optional[str] = datetime.datetime.now().isoformat()
    created_at: Optional[DateTime] = None
    content: Optional[str] = None
    president: Optional[str] = None
    summary: Optional[str] = None


class ArticleChunk(BaseModel):
    id: int = 0
    article_id: int
    chunk: str
    chunk_id: int
    embedding: list[float] = conlist(float, min_length=1536, max_length=1536)
    created_at: DateTime
    president: str

    class Config:
        orm_mode = True


class ArticleChunkResult(BaseModel):
    """Model for an article chunk result"""

    article_id: int
    chunk: str
    chunk_id: int
    article_title: str
    created_at: DateTime
    distance: float
    score: float
    cosine_distance: float

    class Config:
        orm_mode = True


class ArticleRankType(BaseModel):
    id: int
    title: str
    link: str
    body: str
    created_at: DateTime
    total_rank: float

    class Config:
        orm_mode = True


class ArticleSummaryResult(BaseModel):
    id: int
    title: str
    summary: str
    created_at: DateTime

    class Config:
        orm_mode = True


class ArticleChunkSearchResult(BaseModel):
    article_id: int
    chunk: str
    chunk_id: int
    created_at: DateTime
    search_rank: float

    class Config:
        orm_mode = True


class ArticleSummarySearchResult(BaseModel):
    title: str
    summary: str
    created_at: DateTime

    class Config:
        orm_mode = True


# CREATE OR REPLACE FUNCTION hybrid_vector_fulltext_search(
#     search_term TEXT,
#     embedding_vector VECTOR,
#     num_chunks INTEGER = 10,
#     rrf_k INTEGER = 60
# )
# RETURNS TABLE(article_id INTEGER, chunk_id INTEGER, chunk TEXT, created_at TIMESTAMP, combined_score FLOAT) AS $$


class HybridVectorFullTextSearchResult(BaseModel):
    article_id: int
    chunk_id: int
    chunk: str
    created_at: DateTime
    combined_score: float

    class Config:
        orm_mode = True
