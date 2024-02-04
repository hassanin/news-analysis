""" This module contains the models for the RSS feed and articles. """
from typing import Optional
import xml.etree.ElementTree as ET
from pydantic import BaseModel


class FeedHeader(BaseModel):
    """Model for the RSS feed header"""

    title: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    last_build_date: Optional[str] = None
    pub_date: Optional[str] = None
    # image url is an optional string
    image_url: Optional[str] = None


class Article(BaseModel):
    """Model for an RSS feed article"""

    title: Optional[str] = None
    link: Optional[str] = None
    guid: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    pub_date: Optional[str] = None
    content: Optional[str] = None


def parse_rss_feed(feed_xml: str) -> (FeedHeader, list[Article]):
    """Parse the RSS feed XML string into a FeedHeader and list of Articles"""
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")

    # Parse feed header
    title = getattr(channel.find("title"), "text", "Default Title")
    link = getattr(channel.find("link"), "text", "Default Link")
    description = getattr(channel.find("description"), "text", "Default Description")
    language = getattr(channel.find("language"), "text", "Default Language")
    last_build_date = getattr(
        channel.find("lastBuildDate"), "text", "Default Last Build Date"
    )
    pub_date = getattr(channel.find("pubDate"), "text", "Default Pub Date")
    image_url = getattr(channel.find("image/url"), "text", "Default Image URL")

    # title = channel.find("title").text
    # link = channel.find("link").text
    # description = channel.find("description").text
    # language = channel.find("language").text
    # copyright = channel.find("copyright").text
    # last_build_date = channel.find("lastBuildDate").text
    # pub_date = channel.find("pubDate").text
    # image_url = channel.find("image/url").text

    header = FeedHeader(
        title=title,
        link=link,
        description=description,
        language=language,
        # copyright,
        last_build_date=last_build_date,
        pub_date=pub_date,
        image_url=image_url,
    )

    # Parse articles
    articles = []
    for item in channel.findall("item"):
        # article_title = item.find("title").text
        # article_link = item.find("link").text
        # guid = item.find("guid").text
        # article_description = item.find("description").text
        # creator = item.find("{http://purl.org/dc/elements/1.1/}creator").text
        # article_pub_date = item.find("pubDate").text
        # categories = [category.text for category in item.findall("category")]
        # image_url = item.find('{http://search.yahoo.com/mrss/}content').get('url')
        # image_credit = '' #item.find('{http://search.yahoo.com/mrss/}credit').text
        # image_description = item.find('{http://search.yahoo.com/mrss/}description').text

        article_title = getattr(item.find("title"), "text", "Default Article Title")
        article_link = getattr(item.find("link"), "text", "Default Article Link")
        guid = getattr(item.find("guid"), "text", "Default Article Guid")
        article_description = getattr(
            item.find("description"), "text", "Default Article Description"
        )
        creator = getattr(
            item.find("{http://purl.org/dc/elements/1.1/}creator"),
            "text",
            "Default Article Creator",
        )
        article_pub_date = getattr(
            item.find("pubDate"), "text", "Default Article Pub Date"
        )
        content = getattr(item.find("content"), "text", "")
        # categories = [category.text for category in item.findall("category")]
        # categories = []
        # image_url = ""
        # image_credit = ""
        # image_description = ""

        article = Article(
            title=article_title,
            link=article_link,
            guid=guid,
            description=article_description,
            creator=creator,
            pub_date=article_pub_date,
            content=content,
            # categories=categories,
            # image_url=image_url,
            # image_credit=image_credit,
            # image_description=image_description,
        )
        articles.append(article)

    return header, articles


# Example usage
def try_out():
    with open("response3.xml", "r", encoding="utf8") as f:
        rss_feed_xml = f.read()

    header, articles = parse_rss_feed(rss_feed_xml)

    print("Feed Title:", header.title)
    for article in articles:
        print("Article Title:", article.title)
    # rss_feed_xml = """<rss ...> ... </rss>"""  # Replace with actual RSS feed XML string
    # header, articles = parse_rss_feed(rss_feed_xml)

    # print("Feed Title:", header.title)
    # for article in articles:
    #     print("Article Title:", article.title)
