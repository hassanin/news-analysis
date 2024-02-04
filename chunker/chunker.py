# Performs chunking of the input text
from whitehouse.database import get_all_articles, insert_article_chunk
from myopenai.embedding import create_embedding
from whitehouse.models import ArticleChunk
import tqdm

def chunk_text(text:str, chunk_size:int = 2000)-> list[str]:
    """Performs chunking of the input text"""
    # first check if the chunk size is less than the length of the text
    if chunk_size > len(text):
        return [text]
   # python hanldes the last chunk by default even if it is less than the chunk size
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# We will write a function that reads the articles from the database
# And for each article perform chunking and for each chunk we will 
# perform the embedding and then we will save the embeddings to the database along with the chunk
def perform_open_ai_insertion():
    # get all the articles from the database
    articles = get_all_articles()
    # for each article, chunk the text and perform the embedding
    for article in tqdm.tqdm(articles):
        chunks = chunk_text(article.content)
        for idx, chunk in enumerate(chunks):
            # perform the embedding
            embedding = create_embedding(chunk)
            print(embedding[:10])
            # save the embedding to the database
            # print the first 10 elements of the embedding
            article_chunk= ArticleChunk(article_id=article.id, chunk=chunk, embedding=embedding, created_at=article.created_at,chunk_id=idx)
            insert_article_chunk(article_chunk)
            