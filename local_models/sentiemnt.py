from transformers import pipeline
from pydantic import BaseModel

sentiment_pipeline = pipeline("sentiment-analysis")


class SentimentResult(BaseModel):
    """Model for the sentiment result"""

    label: str
    score: float


def perform_sentiment_analysis(data: list[str]) -> list[SentimentResult]:
    """Perform some trials"""
    res = sentiment_pipeline(data)
    # print(res)
    res2: list[SentimentResult] = []
    for item in res:
        res2.append(SentimentResult(label=item["label"], score=item["score"]))
    return res2
