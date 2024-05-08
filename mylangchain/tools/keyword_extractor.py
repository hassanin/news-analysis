from langchain.tools import tool

from myopenai.chatbot import ChatBot


@tool
def extract_keywords_from_text(text: str) -> str:
    """Extract keywords from the text"""
    chat_bot = ChatBot("You are a tool to extract keywords from text")
    res = chat_bot.add_chatbot_message(f"Extract keywords from text: {text}")
    return res
