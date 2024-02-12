from .parser import get_all_links, test_call_one_article, load_all_links
from .database import insert_data_into_database

def trump_entrypoint():
    print("in getting all links")
    # load_all_links()
    insert_data_into_database()
    # get_all_links()
    # test_call_one_article()
