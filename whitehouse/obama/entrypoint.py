from .parser import get_all_links, test_call_one_article, load_all_links
from .database import insert_data_into_database


def obama_entrypoint():
    print("in getting all links")
    # load_all_links()
    # get_all_links()
    # test_call_one_article()
    insert_data_into_database()
