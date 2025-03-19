from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RawReview(BaseModel):
    app_id: str = Field(..., description="App identifier")
    review_text: str = Field(..., description="Raw review text")
    review_title: str = Field("", description="Review title")
    rating: int = Field(..., ge=1, le=5, description="Review rating (1-5)")
    date_scraped: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when review was scraped")
    
    class Config:
        schema_extra = {
            "example": {
                "app_id": "1459969523",
                "review_text": "🔥 Love it! Best horoscope app.",
                "review_title": "Amazing App!",
                "rating": 5,
                "date_scraped": "2024-03-17T12:00:00Z"
            }
        }

class ProcessedReview(BaseModel):
    app_id: str = Field(..., description="App identifier")
    review_text: str = Field(..., description="Processed review text")
    review_title: str = Field("", description="Processed review title")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment analysis score (-1 to 1)")
    sentiment: str = Field(..., description="Sentiment label (POSITIVE, NEGATIVE)")
    date_processed: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when review was processed")
    
    class Config:
        schema_extra = {
            "example": {
                "app_id": "1459969523",
                "raw_review_text": "🔥 Love it! Best horoscope app.",
                "raw_review_title": "Amazing App!",
                "processed_review_text": "Love it! Best horoscope app.",
                "processed_review_title": "Amazing App!",
                "sentiment_score": 0.9,
                "sentiment": "POSITIVE",
                "date_processed": "2024-03-17T12:00:00Z"
            }
        }

class ReviewMetrics(BaseModel):
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    average_rating: float
    rating_distribution: dict[str, int]
    total_reviews: int
    review_length_stats: dict[str, float]
    overall_sentiment: str
    overall_sentiment_score: float
    sentiment_distribution: dict[str, int]
    
    class Config:
        schema_extra = {
            "example": {
                "last_updated": "2024-03-17T12:00:00Z",
                "average_rating": 4.5,
                "rating_distribution": {
                    "0": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 100
                },
                "total_reviews": 100,
                "review_length_stats": {
                    "min": 10,
                    "max": 1000,
                    "avg": 100.5
                },
                "overall_sentiment": "POSITIVE",
                "overall_sentiment_score": 0.8,
                "sentiment_distribution": {
                    "POSITIVE": 80,
                    "NEGATIVE": 20
                }
            }
        }

class ReviewResponse(BaseModel):
    status: str
    message: str
    data: List[ProcessedReview]

class RawReviewResponse(BaseModel):
    status: str
    message: str
    data: List[Dict[str, Any]]

class MetricsResponse(BaseModel):
    status: str
    message: str
    data: ReviewMetrics 