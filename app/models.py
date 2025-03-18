from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RawReview(BaseModel):
    app_id: str = Field(..., description="App identifier")
    app_name: str = Field(..., description="Name of the app")
    review_text: str = Field(..., description="Raw review text")
    rating: int = Field(..., ge=1, le=5, description="Review rating (1-5)")
    date_scraped: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when review was scraped")
    
    class Config:
        schema_extra = {
            "example": {
                "app_id": "1459969523",
                "app_name": "Nebula Horoscope",
                "review_text": "🔥 Love it! Best horoscope app.",
                "rating": 5,
                "date_scraped": "2024-03-17T12:00:00Z"
            }
        }

class ProcessedReview(BaseModel):
    app_id: str = Field(..., description="App identifier")
    cleaned_text: str = Field(..., description="Processed review text")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment analysis score (-1 to 1)")
    sentiment: str = Field(..., description="Sentiment label (POSITIVE, NEGATIVE, NEUTRAL)")
    sentiment_confidence: float = Field(..., ge=0, le=1, description="Confidence score for sentiment analysis (0 to 1)")
    date_processed: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when review was processed")
    
    class Config:
        schema_extra = {
            "example": {
                "app_id": "1459969523",
                "cleaned_text": "Love it! Best horoscope app.",
                "sentiment_score": 0.9,
                "sentiment": "POSITIVE",
                "sentiment_confidence": 0.917,
                "date_processed": "2024-03-17T12:00:00Z"
            }
        }

class ReviewMetrics(BaseModel):
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    average_rating: float
    rating_distribution: dict[str, int]
    total_reviews: int
    review_length_stats: dict[str, float]
    length_rating_correlation: float
    
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
                "length_rating_correlation": 0.2
            }
        } 