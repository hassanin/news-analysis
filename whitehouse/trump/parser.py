from datetime import date
import datetime
from re import A
import requests
from bs4 import BeautifulSoup
from ..models import Article
from tqdm import tqdm

def get_all_links():
    """Get all links from the API"""
    max_num = 910
    # https://www.whitehouse.gov/briefing-room/page/941/
    # url_template = "https://obamawhitehouse.archives.gov/briefing-room/statements-and-releases?term_node_tid_depth=41&page="
    url_template = "https://trumpwhitehouse.archives.gov/news/page/"
    # url_template = "https://obamawhitehouse.archives.gov/briefing-room/presidential-actions?term_node_tid_depth=46&page="
    all_links = set()
    file_name = "all_links_trump.txt"
    filters=['presidential-actions','briefings-statements','articles','press-briefings','statements-releases','remarks','executive-orders','proclamations','presidential-memoranda','presidential-actions','presidential-nominations']
    with open(file_name, "a", encoding="utf8") as f:
        # for link in all_links:
        #     f.write(link + "\n")
        for i in tqdm(range(0, max_num)):
            url = f"{url_template}{i}/"
            print(url)
            response = requests.get(url, timeout=5)
            # print(response.text)
            # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            # Use a Hash Set to store the links
            cutoff_character_count =  len("https://trumpwhitehouse.archives.gov/") + 25
            for link in links:
                # if link["href"].startswith(
                #     "/the-press-office"
                # ):
                # check if the link is in the filters
                if any(x in link["href"] for x in filters) and len(link["href"]) > cutoff_character_count:
                #     # take only links with character count greater than cutoff_character_count
                #     if len(link["href"]) > cutoff_character_count:
                    extracted_link = link["href"]
                    full_link=f'{extracted_link}'
                    print(full_link)
                    f.write(full_link + "\n")
                    all_links.add(full_link)
            # exit()
    # save the links to a file
    


# load all the links from the file
def load_all_links(file_name: str = "all_links_trump.txt"):
    """Load all links from the file"""
    index = 0
    data_dir = "data/whitehouse/Trump/"
    with open(file_name, "r", encoding="utf8") as f:
        for line in f:
            # if index < 3041:
            #     index += 1
            #     continue
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
article1 = "https://trumpwhitehouse.archives.gov/briefings-statements/text-notice-continuation-national-emergency-respect-southern-border-of-the-united-states/"

def test_call_one_article():
    """Test calling one article"""
    file_location = "article2.txt"
    get_artictle_content(article1, file_location)


def get_artictle_content(aritcle_url: str, file_location: str):
    """Get the content of the article"""
    response = requests.get(aritcle_url, timeout=5)
    # print(response.text)
    # save the response to a file
    file_name = "response_article_5.html"
    with open(file_name, "w", encoding="utf8") as f:
        f.write(response.text)
    # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
    soup = BeautifulSoup(response.text, "html.parser")
    # <main id="main-content">    
    content = soup.find("main", id="main-content").find_all("p")
    # get the content as a string by extracting the text from each <p> tag
    content_string = ''
    for p in content:
        content_string += p.text
    # get the time stamp
    time_stamp = soup.find("time").text
    # if time_Stamp is not None, convert it to a datetime object
    try:
        time_stamp = datetime.datetime.strptime(time_stamp, "%B %d, %Y")
    except Exception as e:
        print(e)
        time_stamp = None
    # time_stamp = None
    # print(f'time_stamp: {time_stamp}')
    # get the title from the <title> tag
    title = soup.find("title").text
    article: Article = Article(
        title=title, link=aritcle_url, created_at=time_stamp, content=content_string
    )
    # print(article.model_dump())
    with open(file_location, "w", encoding="utf8") as f:
        # Make the JSON pretty
        f.write(article.model_dump_json(indent=4))
