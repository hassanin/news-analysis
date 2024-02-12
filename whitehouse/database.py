import datetime
import os

from httpx import get
from .models import (
    Article,
    ArticleChunk,
    ArticleChunkResult,
    ArticleChunkSearchResult,
    ArticleRankType,
)
from psycopg import connect, sql
from pgvector.psycopg import register_vector

# Database connection parameters
params = {
    "dbname": "newsanalysis",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
}

# Establishing the connection
conn = connect(**params)
register_vector(conn)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")


def insert_data_into_database():
    """Insert data into the database"""
    # read each article from JSON
    data_dir = "data/whitehouse/Biden/"
    # read each file in the data directory
    for file_name in os.listdir(data_dir):
        file_location = f"{data_dir}{file_name}"
        with open(file_location, "r", encoding="utf8") as f:
            article_json = f.read()
        # print(article_json)
        article = Article.model_validate_json(article_json)
        # article.created_at = datetime.datetime.now()
        # set the created_at if it is null to the current time
        # print(article)
        # insert the article into the database
        insert_article(article)
        # break


def insert_article(article: Article):
    """Insert the article into the database"""
    with conn.cursor() as cur:
        query = sql.SQL(
            "INSERT INTO article (title, link, created_at, body, president) VALUES (%s, %s, %s, %s, %s)"
        )
        cur.execute(
            query,
            (
                article.title,
                article.link,
                article.created_at,
                article.content,
                article.president,
            ),
        )
        conn.commit()


def get_all_articles() -> list[Article]:
    """Get all the articles from the database"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT id, title, link, body, created_at FROM article")
        cur.execute(query)
        articles = cur.fetchall()
        # print the articles
        articles_typed: list[Article] = []
        for article in articles:
            # map the article to the Article model
            articles_typed.append(
                Article(
                    id=article[0],
                    title=article[1],
                    link=article[2],
                    content=article[3],
                    created_at=article[4],
                )
            )
            # print(article)
        return articles_typed


def search_articles(search_term: str) -> list[ArticleRankType]:
    """Search the articles for the search term"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT * FROM search_articles(%s)")
        cur.execute(query, (f"%{search_term}%",))
        articles = cur.fetchall()
        results: list[ArticleRankType] = []
        # print the articles
        for article in articles:
            # print(article)
            results.append(
                ArticleRankType(
                    id=article[0],
                    title=article[1],
                    link=article[2],
                    body=article[3],
                    created_at=article[4],
                    total_rank=article[5],
                )
            )
        return results


def search_article_chunks(
    search_term: str, num_results: int = 20
) -> list[ArticleChunkSearchResult]:
    """Search the article chunks for the search term"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT * FROM search_article_chunks(%s, %s::int)")
        cur.execute(query, (f"%{search_term}%", num_results))
        articles = cur.fetchall()
        results: list[ArticleChunkSearchResult] = []
        # print the articles
        for article in articles:
            # print(article)
            results.append(
                ArticleChunkSearchResult(
                    article_id=article[0],
                    chunk=article[1],
                    chunk_id=article[2],
                    created_at=article[3],
                    search_rank=article[4],
                )
            )
        return results


def insert_article_chunk(article_chunk: ArticleChunk):
    """Insert the article chunk into the database"""
    with conn.cursor() as cur:
        query = sql.SQL(
            "INSERT INTO article_chunk (article_id, chunk, chunk_id, embedding, created_at) VALUES (%s, %s, %s, %s, %s)"
        )
        cur.execute(
            query,
            (
                article_chunk.article_id,
                article_chunk.chunk,
                article_chunk.chunk_id,
                article_chunk.embedding,
                article_chunk.created_at,
            ),
        )
        conn.commit()


def perform_vector_search(
    embedding: list[float], num_results: int = 10
) -> list[ArticleChunkResult]:
    """Perform vector search"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT * FROM get_similar_chunks(%s::vector(1536), %s::int) ")
        cur.execute(query, (embedding, num_results))
        articles = cur.fetchall()
        # print the articles
        articles_result: list[ArticleChunkResult] = []
        for article in articles:
            # print(article)
            articles_result.append(
                ArticleChunkResult(
                    article_id=article[0],
                    chunk=article[1],
                    chunk_id=article[2],
                    article_title=article[3],
                    created_at=article[4],
                    distance=article[5],
                )
            )
        return articles_result


def trials():
    articles = get_all_articles()
    print(f"first article: {articles[0]}")


# # Create a cursor object
#         cur = conn.cursor()

#         # Execute the stored procedure
#         cur.callproc('search_articles', [search_text])

#         # Fetch all the rows
#         rows = cur.fetchall()

#         # Close communication with the database
#         cur.close()
