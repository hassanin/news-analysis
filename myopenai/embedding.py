"""Create an embedding from a text string."""

import openai


def create_embedding(text: str) -> list[float]:
    """Create an embedding from a text string."""
    response = openai.embeddings.create(input=text, model="adaembedding1")
    embeddings = response.data[0].embedding
    # embeddings = response["data"][0]["embedding"]
    # print(len(embeddings))
    return embeddings
