from re import A
import requests
from bs4 import BeautifulSoup
from .models import Article


def get_all_links():
    """Get all links from the API"""
    max_num = 941
    # https://www.whitehouse.gov/briefing-room/page/941/
    url_template = "https://www.whitehouse.gov/briefing-room/page/"
    all_links = set()
    for i in range(1, max_num + 1):
        url = f"{url_template}{i}/"
        print(url)
        response = requests.get(url, timeout=5)
        # print(response.text)
        # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        # Use a Hash Set to store the links
        cutoff_character_count = len("https://www.whitehouse.gov/briefing-room/") + 10
        for link in links:
            if link["href"].startswith("https://www.whitehouse.gov/briefing-room/"):
                # take only links with character count greater than cutoff_character_count
                if len(link["href"]) > cutoff_character_count:
                    # print(link["href"])
                    all_links.add(link["href"])
    # save the links to a file
    file_name = "all_links.txt"
    with open(file_name, "w", encoding="utf8") as f:
        for link in all_links:
            f.write(link + "\n")


# load all the links from the file
def load_all_links(file_name: str = "all_links.txt"):
    """Load all links from the file"""
    index = 0
    data_dir = "data/whitehouse/Biden/"
    with open(file_name, "r", encoding="utf8") as f:
        for line in f:
            if index < 3041:
                index += 1
                continue
            try:
                url = line.strip()
                print(f"Processing {index}: {url}")
                # for each url, get the content and save it to a file
                file_location = f"{data_dir}article{index}.json"
                get_artictle_content(url, file_location)
            except Exception as e:
                print(e)
            index += 1


# article1 = "https://www.whitehouse.gov/briefing-room/statements-releases/2024/01/25/white-house-announces-new-actions-to-promote-safe-storage-of-firearms/"
# article1 = "https://www.whitehouse.gov/briefing-room/statements-releases/2024/01/26/statement-from-president-joe-biden-on-the-bipartisan-senate-border-security-negotiations/"
# https://www.whitehouse.gov/briefing-room/statements-releases/2024/01/25/white-house-announces-new-actions-to-promote-safe-storage-of-firearms/
# article1 = "https://trumpwhitehouse.archives.gov/briefings-statements/statement-press-secretary-regarding-executive-grants-clemency-012021/"
article1 = "https://www.whitehouse.gov/briefing-room/blog/2023/12/22/in-2023-president-bidens-investing-in-america-agenda-delivered-results-for-american-families/"


def test_call_one_article():
    """Test calling one article"""
    file_location = "article1.txt"
    get_artictle_content(article1, file_location)


def get_artictle_content(aritcle_url: str, file_location: str):
    """Get the content of the article"""
    response = requests.get(aritcle_url, timeout=5)
    # print(response.text)
    # # save the response to a file
    # file_name = "response_article_2.html"
    # with open(file_name, "w", encoding="utf8") as f:
    #     f.write(response.text)
    # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
    soup = BeautifulSoup(response.text, "html.parser")
    # # Get all <p> tags
    # content = soup.find_all("p")
    # get all <section class="body-content"> tags
    # get the pargraphs nestedinside the <section class="body-content"> tags
    content = soup.find("section", class_="body-content").find_all("p")
    # get the content as a string by extracting the text from each <p> tag
    content_string = ""
    for p in content:
        content_string += p.text
    # get the time stamp
    time_stamp = soup.find("time", class_="published").text
    # print(time_stamp)
    # get the title from the <title> tag
    title = soup.find("title").text
    article: Article = Article(
        title=title, link=aritcle_url, pub_date=time_stamp, content=content_string
    )
    with open(file_location, "w", encoding="utf8") as f:
        # Make the JSON pretty
        f.write(article.model_dump_json(indent=4))
