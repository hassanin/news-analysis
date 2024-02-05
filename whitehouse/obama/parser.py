from re import A
import requests
from bs4 import BeautifulSoup
from ..models import Article
from tqdm import tqdm

def get_all_links():
    """Get all links from the API"""
    max_num = 177
    # https://www.whitehouse.gov/briefing-room/page/941/
    # url_template = "https://obamawhitehouse.archives.gov/briefing-room/statements-and-releases?term_node_tid_depth=41&page="
    url_template = "https://obamawhitehouse.archives.gov/briefing-room/press-briefings?term_node_tid_depth=36&page="
    # url_template = "https://obamawhitehouse.archives.gov/briefing-room/presidential-actions?term_node_tid_depth=46&page="
    all_links = set()
    file_name = "all_links_obama.txt"
    with open(file_name, "a", encoding="utf8") as f:
        # for link in all_links:
        #     f.write(link + "\n")
        for i in tqdm(range(0, max_num)):
            url = f"{url_template}{i}"
            print(url)
            response = requests.get(url, timeout=5)
            # print(response.text)
            # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            # Use a Hash Set to store the links
            cutoff_character_count =  1
            for link in links:
                if link["href"].startswith(
                    "/the-press-office"
                ):
                #     # take only links with character count greater than cutoff_character_count
                #     if len(link["href"]) > cutoff_character_count:
                    extracted_link = link["href"]
                    full_link=f'https://obamawhitehouse.archives.gov{extracted_link}'
                    print(full_link)
                    f.write(full_link + "\n")
                    all_links.add(full_link)
        # exit()
    # save the links to a file
    


# load all the links from the file
def load_all_links(file_name: str = "all_links_obama.txt"):
    """Load all links from the file"""
    index = 0
    data_dir = "data/whitehouse/Obama/"
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
article1 = "https://obamawhitehouse.archives.gov/the-press-office/presidential-records"

def test_call_one_article():
    """Test calling one article"""
    file_location = "article2.txt"
    get_artictle_content(article1, file_location)


def get_artictle_content(aritcle_url: str, file_location: str):
    """Get the content of the article"""
    response = requests.get(aritcle_url, timeout=5)
    # print(response.text)
    # # save the response to a file
    # file_name = "response_article_4.html"
    # with open(file_name, "w", encoding="utf8") as f:
    #     f.write(response.text)
    # using beautiful soup, get all the linksthat start with https://www.whitehouse.gov/breifing-room/
    soup = BeautifulSoup(response.text, "html.parser")
    # # Get all <p> tags
   
    # the content is in a div with id <div id="content-start" , get all text from it
    content_div = soup.find('div', id='content-start')
    # content = soup.find("content-start")
    # Get all text from content
    content_string = content_div.text
    # print(content_string)
    # exit()
    # get the time stamp
    # time_stamp = soup.find("time", class_="published").text
    # # print(time_stamp)
    # # get the title from the <title> tag
    title = soup.find("title").text
    # print(f'Title: {title} and time ')
    article: Article = Article(
        title=title, link=aritcle_url, pub_date=None, content=content_string
    )
    with open(file_location, "w", encoding="utf8") as f:
        # Make the JSON pretty
        f.write(article.model_dump_json(indent=4))
