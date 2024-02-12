from local_models import sentiemnt
from whitehouse.database import perform_vector_search
from whitehouse.models import ArticleChunkResult
from .embedding import create_embedding
from chunker.code_analysis import calaculate_tokens_aux
from local_models.sentiemnt import perform_sentiment_analysis


def answer_question(question: str) -> list[ArticleChunkResult]:
    """Answer the question using the openai model"""
    # Create the embedding first
    embedding = create_embedding(question)
    results = perform_vector_search(embedding, 20)
    # add result text as a single string
    result_text = ""
    idx = 0
    for result in results:
        print(f" {idx}   {result.model_dump_json()} \n")
        result_text += result.model_dump_json() + " "
        idx += 1
    total_tokens = calaculate_tokens_aux(result_text)
    print(f"Total tokens: {total_tokens}")
    return results


def analyze_all_sentiments(text: str) -> str:

    res = answer_question(text)
    text_arr = [res[i].chunk for i in range(len(res))]
    sentiemnts = perform_sentiment_analysis(text_arr)
    idx = 0
    for sentiment in sentiemnts:
        print(f"{idx}  {sentiment}")
        idx += 1
    # for each result perform sentiment analysis
