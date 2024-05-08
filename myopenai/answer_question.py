from datetime import date
from local_models import sentiemnt
from myopenai.chatbot import ChatBot
from myopenai.google_chatbot import GoogleChatbot

from whitehouse.database import perform_vector_search
from whitehouse.models import ArticleChunkResult
from .embedding import create_embedding
from chunker.code_analysis import calaculate_tokens_aux
from local_models.sentiemnt import perform_sentiment_analysis


def get_question_segemnts(
    question: str, max_results: int = 10
) -> list[ArticleChunkResult]:
    """Answer the question using the openai model"""
    # Create the embedding first
    embedding = create_embedding(question)
    results = perform_vector_search(embedding, max_results)
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


def answer_question(question: str) -> str:
    """Answer the question using the openai model"""
    res = get_question_segemnts(question, max_results=10)
    result_text = ""
    for result in res:
        result_text += result.model_dump_json() + " "
    date_time_now = date.today()
    chat_bot: ChatBot = ChatBot(
        system_message=f"""You are an AI system whose purpose is to answer questions, today's date is {date_time_now} 
                               and provide answers based on the following data sources: and provide the article title(s) 
                               where the information was found. the created_at field of the article is the data of publication"""
    )
    question_answer = chat_bot.add_chatbot_message(
        f"the data sources are {result_text} and the question is {question}"
    )
    return question_answer


def answer_question_google(question: str) -> str:
    """Answer the question using the openai model"""
    res = get_question_segemnts(question, max_results=10)
    result_text = ""
    for result in res:
        result_text += result.model_dump_json() + " "
    date_time_now = date.today()
    chat_bot: GoogleChatbot = GoogleChatbot(
        system_message="""You are an AI system whose purpose is to answer questions, 
                               and provide answers based on the provided data sources: and provide the article title(s) 
                               where the information was found. the created_at field of the article is the data of publication"""
    )
    question_answer = chat_bot.add_chatbot_message(
        f"the data is {result_text} and the question is {question}"
    )
    return question_answer


def analyze_all_sentiments(text: str) -> str:

    res = get_question_segemnts(text)
    text_arr = [res[i].chunk for i in range(len(res))]
    sentiemnts = perform_sentiment_analysis(text_arr)
    idx = 0
    for sentiment in sentiemnts:
        print(f"{idx}  {sentiment}")
        idx += 1
    # for each result perform sentiment analysis
