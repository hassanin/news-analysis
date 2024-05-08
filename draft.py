from whitehouse.database import (
    search_hybrid_vector_fulltext,
    perform_vector_search,
    search_article_chunks,
)
from myopenai.embedding import create_embedding


def try_hybrid(search_question: str):
    embedding = create_embedding(search_question)
    query1 = "Us Egypt 2014"
    res = search_hybrid_vector_fulltext(query1, embedding, rrf_k=10, vector_weight=1.2)
    # res = search_hybrid_vector_fulltext(search_question, embedding)
    for r in res:
        print(
            f" article_id {r.article_id}: chunk_id: {r.chunk_id}: score: {r.combined_score} {r.chunk},  \n"
        )
    try_keyword(search_question)
    try_vector(search_question)


def try_keyword(search_question: str):
    query1 = "Us Egypt 2014"
    res = search_article_chunks(query1, 10)
    # res = search_hybrid_vector_fulltext(search_question, embedding)
    print(f"results for keyword search")
    article_ids = [str(r.article_id) for r in res]
    print(f" {', '.join(article_ids)}: \n")


def try_vector(search_question: str):
    embedding = create_embedding(search_question)
    res = perform_vector_search(embedding)
    # res = search_hybrid_vector_fulltext(search_question, embedding)
    print(f"results for vector search")
    # convert the article_ids into a list and display the list as a string
    article_ids = [str(r.article_id) for r in res]
    print(f" {', '.join(article_ids)}: \n")
