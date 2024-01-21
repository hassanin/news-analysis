# from re import search
"""File to run the program"""
import os
import requests

def main():
    print("hello world")
    get_all_articles()


def get_all_articles():
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
