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
    """Model for storing review metrics."""
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    average_rating: float
    rating_distribution: Dict[str, float]  # distribution of ratings (1-5) as percentages
    total_reviews: int
    review_length_stats: Dict[str, float]  # min, max, avg lengths

    class Config:
        schema_extra = {
            "example": {
                "last_updated": "2024-03-20T12:00:00",
                "average_rating": 4.5,
                "rating_distribution": {
                    "1": 5.0,
                    "2": 10.0,
                    "3": 15.0,
                    "4": 30.0,
                    "5": 40.0
                },
                "total_reviews": 100,
                "review_length_stats": {
                    "min": 10,
                    "max": 500,
                    "avg": 150.5
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

class InsightsMetrics(BaseModel):
    """Model for storing NLP-based insights metrics."""
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    overall_sentiment: str
    sentiment_score: float
    sentiment_distribution: Dict[str, int]
    negative_keywords: List[str]
    improvement_areas: List[str]
    wordcloud_image: str = Field(default="")

    class Config:
        schema_extra = {
            "example": {
                "last_updated": "2024-03-20T12:00:00",
                "overall_sentiment": "POSITIVE",
                "sentiment_score": 0.85,
                "sentiment_distribution": {
                    "POSITIVE": 80,
                    "NEGATIVE": 20
                },
                "negative_keywords": ["crash", "slow", "bug"],
                "improvement_areas": [
                    "Address issues related to 'crash'",
                    "Address issues related to 'slow'",
                    "Address issues related to 'bug'"
                ],
                "wordcloud_image": "data:image/png;base64,..."
            }
        }

class MetricsResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = Field(
        ...,
        description="Dictionary containing both review metrics and insights metrics",
        example={
            "metrics": {
                "last_updated": "2024-03-20T12:00:00",
                "average_rating": 4.5,
                "rating_distribution": {
                    "1": 5,
                    "2": 10,
                    "3": 15,
                    "4": 30,
                    "5": 40
                },
                "total_reviews": 100,
                "review_length_stats": {
                    "min": 10,
                    "max": 500,
                    "avg": 150.5
                }
            },
            "insights": {
                "last_updated": "2024-03-20T12:00:00",
                "overall_sentiment": "POSITIVE",
                "sentiment_score": 0.8,
                "sentiment_distribution": {
                    "POSITIVE": 80,
                    "NEGATIVE": 20
                },
                "negative_keywords": ["crash", "slow", "bug"],
                "improvement_areas": [
                    "Address issues related to 'crash'",
                    "Address issues related to 'slow'",
                    "Address issues related to 'bug'"
                ]
            }
        }
    ) 