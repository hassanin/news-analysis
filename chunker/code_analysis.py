"""Analyze number of tokens"""

import tiktoken
from whitehouse.database import get_all_articles

# cl100k_base	gpt-4, gpt-3.5-turbo, text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
# p50k_base	Codex models, text-davinci-002, text-davinci-003
# r50k_base (or gpt2)	GPT-3 models like davinci

tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
# print("tiktoken encoder loaded")
# enc1 = tiktoken_encoder.encode("Je suis Malade.")
# print(enc1)
# print(len(enc1))
# exit()


# text_tokens = tiktoken_encoder.encode(text)
# return len(text_tokens)
def calculate_tokens():
    """Reads all articles from the postgres database and calculates the number of tokens"""

    articles = get_all_articles()
    tokens = 0
    idx = 0
    for article in articles:
        tokens += len(tiktoken_encoder.encode(article.content))
        print(f"for idx = {idx} Number of tokens so far: {tokens}")
        idx += 1
    print(f"Total number of tokens: {tokens}")


def calaculate_tokens_aux(text: str):
    """Calculate the number of tokens in a string"""
    return len(tiktoken_encoder.encode(text))
