"""Create an embedding from a text string."""

import openai
import tenacity


def create_embedding(text: str) -> list[float]:
    """Create an embedding from a text string."""
    response = openai.embeddings.create(input=text, model="adaembedding1")
    embeddings = response.data[0].embedding
    # embeddings = response["data"][0]["embedding"]
    # print(len(embeddings))
    return embeddings


@tenacity.retry(wait=tenacity.wait_exponential(2), stop=tenacity.stop_after_attempt(3))
async def create_embedding_async(text: str) -> list[float]:
    client = openai.AsyncAzureOpenAI()
    # print(f"creating embedding article:")
    response = await client.embeddings.create(input=text, model="adaembedding1")
    embeddings = response.data[0].embedding
    return embeddings
