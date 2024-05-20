from myopenai.google_chatbot import GoogleChatbot


def extract_keywords_from_query(query: str) -> str:
    """Extracts the keywords from the query"""
    # split the query into words
    chatbot = GoogleChatbot(
        system_message="Your job is to extract the keywords from the query. so that it can be used in fts applications, return the keywords as a single string separated by a single whitespace"
    )
    res = chatbot.add_chatbot_message(f"query is {query}")
    return res


def example():
    print(extract_keywords_from_query("What is the capital of Egypt?"))
    print(
        extract_keywords_from_query(
            "What is the relationship between US and Egypt in 2014?"
        )
    )
