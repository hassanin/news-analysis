# from re import search
"""File to run the program"""
# # from operator import ge
# from turtle import st
# import langchain_visualizer
from dotenv import load_dotenv

load_dotenv()
from mylangchain.start_agent import start_loop


from whitehouse.database import search_article_chunks, search_articles

# import os
# import requests
# from rss_reader.http import get_rss_feed, get_rss_feed_local_file
# from rss_reader.models import parse_rss_feed, FeedHeader, Article
# from whitehouse.parser import (
#     get_all_links,
#     get_artictle_content,
#     test_call_one_article,
#     load_all_links,
# )
# from whitehouse.database import insert_data_into_database, trials
# from myopenai.examples import try_stuff
from chunker.chunker import perform_open_ai_insertion

# from whitehouse.trump.entrypoint import trump_entrypoint
# from whitehouse.trump.entrypoint import trump_entrypoint
from chunker.code_analysis import calculate_tokens


from myopenai.answer_question import (
    answer_question,
    answer_question_google,
    get_question_segemnts,
    analyze_all_sentiments,
)
from draft import try_hybrid

# from local_models.trials import try_stuff


def main():
    """Main function"""
    print("hello world")
    # try_stuff()
    # trials()
    # perform_open_ai_insertion()
    # trump_entrypoint()
    # calculate_tokens()
    # res = get_question_segemnts("The relationship between the US and Egypt")
    # analyze_all_sentiments("The relationship between the US and Egypt")
    # res = search_articles(" relationship Egypt")
    # # modify the text content to take the first 2000 characters
    # for idx, r in enumerate(res):
    #     r.body = r.body[:1000]
    #     print(f" {idx}: {r.model_dump()} \n")
    # res = search_article_chunks(" relationship Egypt")
    # for idx, r in enumerate(res):
    #     # print(f" {idx}: {r.model_dump()} \n")
    #     print(f" {idx}: {r.article_id}")
    # analyze_all_sentiments("The relationship between the US and China")
    # try_stuff()
    # res = answer_question(
    #     " What were the outcomes of the last US Africa Leaders Summit"
    # )
    # res = answer_question(" When was The Last Japanese Prime Minister to visit the US")
    # res = answer_question_google(
    #     " When was The Last Japanese Prime Minister to visit the US"
    # )
    # res = answer_question("When was the Last time President Biden visited Egypt")
    # res = answer_question_google("When was the Last time a US president visited Egypt")
    # print(res)
    # start_loop()

    # async def start_loop_async23():
    #     start_loop()
    try_hybrid("The relationship between the US and Egypt in 2014")

    # langchain_visualizer.visualize(start_loop_async23)
    # perform_ope
    # n_ai_insertion()
    # rss_feed_example()
    # get_all_links()
    # load_all_links()
    # insert_data_into_database()
    # get_artictle_content()
    # test_call_one_article()


# def rss_feed_example():
#     """Example of getting the RSS feed"""
#     # rss_feed = get_rss_feed()
#     rss_feed = get_rss_feed_local_file()
#     header, articles = parse_rss_feed(rss_feed)
#     print(header)
#     # for each article,display its title and description
#     for article in articles:
#         # print(f"Title: {article.title}")
#         # print(f"Description: {article.description}")
#         # print(f"Guid: {article.guid}")
#         print(article.model_dump())


# def get_all_articles():
#     """Get all articles from the API"""
#     print("get all articles")
#     # convert the request into python using requests library
#     api_key = os.getenv("NEWS_API_KEY")
#     search_term = "Gaza"
#     # url = f'https://newsapi.org/v2/everything?q={search_term}&apiKey={api_key}'
#     # Make url take from and to dates
#     from_date = "2024-01-18"
#     to_date = "2024-01-19"
#     url = f"https://newsapi.org/v2/everything?q={search_term}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={api_key}"
#     print(url)
#     response = requests.get(url, timeout=5)
#     # print(response)
#     # print(response.json())
#     # save the json response to a file
#     with open("response3.json", "w", encoding="utf8") as f:
#         f.write(response.text)


if __name__ == "__main__":
    main()
