import os
import openai
import tenacity

# from openai import AsyncOpenAI

# openai.api_type = "azure"
# # openai.api_base = "https://openaieastcanada.openai.azure.com/"
# openai.api_version = "2023-03-15-preview"
# openai.api_key = os.getenv("OPENAI_API_KEY")


@tenacity.retry(wait=tenacity.wait_exponential(2), stop=tenacity.stop_after_attempt(3))
async def summarize_article(article: str) -> str:
    client = openai.AsyncAzureOpenAI()
    # client = openai.AsyncOpenAI()
    # AsyncAzureOpenAI
    print(f"Summarizing article:")
    try:
        response = await client.chat.completions.create(
            model="gpt-35-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that helps people summarize articles.",
                },
                {"role": "user", "content": f"article is {article}"},
            ],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )
    except Exception as e:
        print(f"Error: {e}")
        # return "Error: Could not summarize the article."
        # rethrow the error
        raise e
    return response.choices[0].message.content


class ChatBot:
    def __init__(
        self,
        system_message: str = "You are an AI assistant that helps people find information.",
    ):
        self._messages = [{"role": "system", "content": system_message}]
        # self._engine = "gpt-4-8k"
        self._engine = "gpt-35-turbo-16k"
        self._temperature = 0.7
        self._max_tokens = 800
        self._top_p = 0.95
        self._frequency_penalty = 0
        self._presence_penalty = 0
        self._stop = None

    def _add_message(self, message: dict[str, str]):
        self._messages.append(message)

    def add_chatbot_message(self, message: str) -> str:
        """Add a message from the chatbot to the chat history.
        Typically executed after"""
        self._add_message({"role": "user", "content": message})
        response = openai.chat.completions.create(
            model=self._engine,
            messages=self._messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
            frequency_penalty=self._frequency_penalty,
            presence_penalty=self._presence_penalty,
            stop=self._stop,
        )

        self._add_message(response.choices[0].message)
        return response.choices[0].message.content

    async def add_chatbot_message_async(self, message: str) -> str:
        client = openai.AsyncOpenAI()
        self._add_message({"role": "user", "content": message})
        response = await client.chat.completions.create(
            model=self._engine,
            messages=self._messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
            frequency_penalty=self._frequency_penalty,
            presence_penalty=self._presence_penalty,
            stop=self._stop,
        )
        return response.choices[0].message.content

    def add_user_message(self, message):
        """Add a message from the user to the chat history."""
        self._messages.append({"role": "user", "content": message})

    def get_chat_history(self):
        """Return the chat history."""
        return self._messages
