import json
from dotenv import load_dotenv

load_dotenv()
from tqdm import tqdm
from openai import chat
from whitehouse.models import Article
import os

from whitehouse.database import (
    get_remaining_all_articles,
    get_all_articles,
    update_article_summary,
    update_article_summary_embedding,
    get_summary_article_results,
)
from myopenai.google_chatbot import generate_text_async, generate_text
from myopenai.chatbot import ChatBot, summarize_article as sa
import asyncio
import tenacity
from myopenai.embedding import create_embedding_async

global count
count = 0


# @tenacity.retry(wait=tenacity.wait_exponential(2), stop=tenacity.stop_after_attempt(3))
async def summarize_article(article: Article, semaphore: asyncio.Semaphore):
    # chatbot = ChatBot("You are an AI assistant that helps people summarize articles.")
    # prompt = f"Summarize this article: {article.content}"
    article_errors_file = "./data/article_errors_embs.txt"
    async with semaphore:
        try:
            # summary = await chatbot.add_chatbot_message_async(prompt)
            # summary = chatbot.add_chatbot_message(prompt)
            # summary = await sa(article.summary)
            summary = await create_embedding_async(article.summary)
            summary_obj = {"embs": summary}
            summary_string = json.dumps(summary_obj)
            with open(
                f"./data/article_embeddings/{article.id}.json", "w", encoding="utf8"
            ) as f:
                f.write(summary_string)
            global count
            count += 1
            print(f"count : { count} summzrized article: {article.title} \n")
            return f"Article: {article.title} \nSummary: {summary} \n\n"
        except Exception as e:
            print(f"Error: {e}")
            with open(article_errors_file, "a", encoding="utf8") as f:
                f.write(f"article_id: {article.id} Error: {e} \n")
            return
        # save the summary as json in './data/article_summaries/{article_id}.json'


async def summarize_all(articles: list[Article]):
    # Schedule all summarize tasks to run concurrently
    semaphore = asyncio.Semaphore(6)
    tasks = [summarize_article(article, semaphore) for article in articles]
    _summaries = await asyncio.gather(*tasks)


async def my_test():
    res = await create_embedding_async("Mohamed is happy")
    print(res)


def insert_data_into_db():
    """Read the json file from the data directory and insert the data into the database"""
    data_dir = "data/article_embeddings/"
    # read each file in the data directory
    for file_name in tqdm(os.listdir(data_dir)):
        file_location = f"{data_dir}{file_name}"
        with open(file_location, "r", encoding="utf8") as f:
            article_summary = f.read()
        # the filename is of the format {article_id}.json, extract article_id from the filename
        article_id = file_name.split(".")[0]
        # print(f"article summary is {article_summary}")
        article_embedding_obj = json.loads(article_summary)
        article_embedding = article_embedding_obj["embs"]
        # print(article_json)
        # article = Article.model_validate_json(article_json)
        # article.created_at = datetime.datetime.now()
        # set the created_at if it is null to the current time
        # print(article)
        # insert the article into the database
        # print(f"inserting article_id: {article_id} summary: {article_summary}")
        update_article_summary_embedding(
            article_id=article_id, summary_embedding=article_embedding
        )
        # break


def main():
    """Main function"""
    # print("hello world")
    # articles = get_all_articles()
    # # res = asyncio.run(my_test())
    # res = asyncio.run(summarize_all(articles))
    insert_data_into_db()
    # res = get_summary_article_results("Egypt", 7, 2013)
    # res_string = " ".join([r.model_dump_json() for r in res])
    # question = "What is the relationship between the US and Egypt?"
    # chatbot = ChatBot()
    # # asnwer = generate_text(
    # #     f"Based on the following data {res_string}, answer {question}"
    # # )
    # answer = chatbot.add_chatbot_message(
    #     f"Based on the following data {res_string}, answer {question}"
    # )
    # print(answer)
    # for r in res:
    #     print(r.model_dump())


if __name__ == "__main__":
    main()
