import datetime
import os

from httpx import get
from ..models import Article, ArticleChunk
from psycopg import connect, sql

# Database connection parameters
params = {
    "dbname": "newsanalysis",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
}

# Establishing the connection
conn = connect(**params)


def insert_data_into_database():
    """Insert data into the database"""
    # read each article from JSON
    data_dir = "data/whitehouse/Trump/"
    # read each file in the data directory
    for file_name in os.listdir(data_dir):
        file_location = f"{data_dir}{file_name}"
        with open(file_location, "r", encoding="utf8") as f:
            article_json = f.read()
        # print(article_json)
        article = Article.model_validate_json(article_json)
        article.president = "Trump"
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
            query, (article.title, article.link, article.created_at, article.content,article.president)
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
            articles_typed.append(Article(id=article[0], title=article[1], link=article[2], content=article[3], created_at=article[4]))
            # print(article)
        return articles_typed

def search_articles(search_term: str):
    """Search the articles for the search term"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT * FROM search_articles(%s)")
        cur.execute(query, (f"%{search_term}%",))
        articles = cur.fetchall()
        
        # print the articles
        for article in articles:
            print(article)
        return articles

def insert_article_chunk(article_chunk:ArticleChunk):
    """Insert the article chunk into the database"""
    with conn.cursor() as cur:
        query = sql.SQL("INSERT INTO article_chunk (article_id, chunk, chunk_id, embedding, created_at) VALUES (%s, %s, %s, %s, %s)")
        cur.execute(query, (article_chunk.article_id, article_chunk.chunk, article_chunk.chunk_id, article_chunk.embedding, article_chunk.created_at))
        conn.commit()
    
def trials():
    articles = get_all_articles()
    print(f'first article: {articles[0]}')
# # Create a cursor object
#         cur = conn.cursor()

#         # Execute the stored procedure
#         cur.callproc('search_articles', [search_text])

#         # Fetch all the rows
#         rows = cur.fetchall()

#         # Close communication with the database
#         cur.close()
