"""Copyright(C) Mohamed Hassanin 2024"""
import requests

urls = ["https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"]
# urls = ["https://feeds.a.dj.com/rss/RSSWorldNews.xml"]


def get_rss_feed() -> str:
    """Get the RSS feed from the given URL"""
    url = urls[0]
    response = requests.get(url, timeout=5)
    res = response.text
    print(res)
    return res


file_path_current = (
    # "nytimes/20121215222929/rss.nytimes.com/services/xml/rss/nyt/World.xml"
    "nytimes/20140421030354/rss.nytimes.com/services/xml/rss/nyt/World.xml"
)


def get_rss_feed_local_file(file_path: str = file_path_current) -> str:
    """Get the RSS feed from the local file"""
    with open(file_path, "r", encoding="utf8") as f:
        res = f.read()
    return res
