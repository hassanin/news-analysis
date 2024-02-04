# from re import search
"""File to run the program"""
# from operator import ge
from dotenv import load_dotenv

load_dotenv()
import os
import requests
from rss_reader.http import get_rss_feed, get_rss_feed_local_file
from rss_reader.models import parse_rss_feed, FeedHeader, Article
from whitehouse.parser import (
    get_all_links,
    get_artictle_content,
    test_call_one_article,
    load_all_links,
)
from whitehouse.database import insert_data_into_database, trials
from myopenai.examples import try_stuff
from chunker.chunker import perform_open_ai_insertion


def main():
    """Main function"""
    print("hello world")
    # try_stuff()
    # trials()
    perform_open_ai_insertion()
    # rss_feed_example()
    # get_all_links()
    # load_all_links()
    # insert_data_into_database()
    # get_artictle_content()
    # test_call_one_article()


def rss_feed_example():
    """Example of getting the RSS feed"""
    # rss_feed = get_rss_feed()
    rss_feed = get_rss_feed_local_file()
    header, articles = parse_rss_feed(rss_feed)
    print(header)
    # for each article,display its title and description
    for article in articles:
        # print(f"Title: {article.title}")
        # print(f"Description: {article.description}")
        # print(f"Guid: {article.guid}")
        print(article.model_dump())


def get_all_articles():
    """Get all articles from the API"""
    print("get all articles")
    # convert the request into python using requests library
    api_key = os.getenv("NEWS_API_KEY")
    search_term = "Gaza"
    # url = f'https://newsapi.org/v2/everything?q={search_term}&apiKey={api_key}'
    # Make url take from and to dates
    from_date = "2024-01-18"
    to_date = "2024-01-19"
    url = f"https://newsapi.org/v2/everything?q={search_term}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={api_key}"
    print(url)
    response = requests.get(url, timeout=5)
    # print(response)
    # print(response.json())
    # save the json response to a file
    with open("response3.json", "w", encoding="utf8") as f:
        f.write(response.text)


if __name__ == "__main__":
    main()
