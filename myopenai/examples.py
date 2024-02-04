from .chatbot import ChatBot
from .embedding import create_embedding


def try_stuff():
    print("Hello, world!")
    chatbot = ChatBot()
    print(chatbot.add_chatbot_message("Hello There , What is the capital of Egypt!"))
    res = create_embedding("Hello, world!")
    print(res)


