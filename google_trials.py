from dotenv import load_dotenv

load_dotenv()
from whitehouse.database import get_remaining_all_articles
from myopenai.google_chatbot import generate_text


def main():
    print("hello world")
    res = generate_text("Hello, what is the capital of France?")
    print(res)
    articles = get_remaining_all_articles()
    for article in articles:

        prompt = f"Summarize this article: {article.content}"
        summary = generate_text(prompt)
        print(f"Article: {article.title} \nSummary: {summary} \n\n")


if __name__ == "__main__":
    main()

