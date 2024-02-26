import google.generativeai as genai
import os
import json

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.0-pro-latest")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
# /home/appuser/.local/lib/python3.10/site-packages/google/generativeai/types/generation_types.py
from google.generativeai.types.generation_types import GenerationConfig


def generate_text(text: str) -> str:
    response = model.generate_content(text)
    print(response)
    return response.text


async def generate_text_async(text: str) -> str:
    response = await model.generate_content_async(text)
    # print(response)
    return response.text


class GoogleChatbot:
    def __init__(
        self,
        system_message: str = "You are an AI assistant that helps people find information.",
    ):
        self._messages = [{"role": "system", "content": system_message}]

    def _add_message(self, message: dict[str, str]):
        self._messages.append(message)

    def add_chatbot_message(self, message: str) -> str:
        """Add a message from the chatbot to the chat history.
        Typically executed after"""
        self._add_message({"role": "user", "content": message})
        # convert messages to a string
        mesages_string = " ".join([json.dumps(m) for m in self._messages])
        # mesages_string = json.dumps(self._messages)
        print(mesages_string)
        config: GenerationConfig = GenerationConfig(temperature=0.1)
        response = model.generate_content(mesages_string, generation_config=config)

        self._add_message(response.text)
        return response.text

    def add_user_message(self, message):
        """Add a message from the user to the chat history."""
        self._messages.append({"role": "user", "content": message})

    def get_chat_history(self):
        """Return the chat history."""
        return self._messages
