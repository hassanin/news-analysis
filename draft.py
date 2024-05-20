from whitehouse.database import (
    search_hybrid_vector_fulltext,
    perform_vector_search,
    search_article_chunks,
    explain_perform_vector_search,
    perform_vector_search_summary,
    search_article_summaries,
)
from myopenai.embedding import create_embedding
from semantic_tools.keyword_extraction import extract_keywords_from_query


def try_hybrid(search_question: str):
    embedding = create_embedding(search_question)
    res = search_hybrid_vector_fulltext(
        search_question,
        embedding,
        rrf_k=10,
        vector_weight=1.0,  # opt_year=2020, opt_month=2
    )
    res = search_hybrid_vector_fulltext(search_question, embedding)
    for r in res:
        print(
            f" article_id {r.article_id}: chunk_id: {r.chunk_id}: score: {r.combined_score} {r.chunk},  \n"
        )
    try_keyword(search_question)
    try_vector(search_question)


def try_keyword(search_question: str):
    keywords = extract_keywords_from_query(search_question)
    res = search_article_chunks(keywords, 10, opt_month=None, opt_year=None)
    # res = search_article_chunks(keywords, 10, opt_month=None, opt_year=2015)
    # res = search_hybrid_vector_fulltext(search_question, embedding)
    print(f"results for keyword search and keyword: {keywords}")
    article_ids = [str(r.article_id) for r in res]
    print(f" {', '.join(article_ids)}: \n")
    for r in res:
        print(
            f" article_id {r.article_id} {r.created_at}: chunk_id: {r.chunk_id}: {r.chunk},  \n"
        )


def try_vector(search_question: str):
    embedding = create_embedding(search_question)
    # res = perform_vector_search(embedding, opt_month=None, opt_year=None)
    res = perform_vector_search_summary(embedding, opt_month=None, opt_year=None)
    for r in res:
        print(
            f" article_id {r.article_id}: {r.distance} {r.created_at} {r.cosine_distance} chunk_id {r.chunk_id}, {r.chunk} \n"
        )
    # res = search_hybrid_vector_fulltext(search_question, embedding)
    print(f"results for vector search")
    # convert the article_ids into a list and display the list as a string
    article_ids = [str(r.article_id) for r in res]
    print(f" {', '.join(article_ids)}: \n")


def explain_search(search_question: str):
    embedding = create_embedding(search_question)
    explain_perform_vector_search(embedding)
