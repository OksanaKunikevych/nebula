from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from pydantic import BaseModel

from app.utils import clean_reviews
from app.metrics import ReviewMetrics
from app.nlp_analysis import InsightAnalysis
from app.api import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="App Store Review Analyzer",
    description="API for analyzing App Store reviews and generating insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routes
app.include_router(router, prefix="/api/v1")

class Review(BaseModel):
    rating: int
    title: Optional[str]
    review_text: str
    date: datetime
    processed: bool = False

class ReviewResponse(BaseModel):
    status: str
    message: str
    data: List[Review]

class RawReviewResponse(BaseModel):
    status: str
    message: str
    data: List[Dict[str, Any]]

class MetricsResponse(BaseModel):
    status: str
    message: str
    data: ReviewMetrics

@app.get("/")
async def root():
    """
    Root endpoint returning API information and available endpoints.
    """
    return {
        "message": "Welcome to App Store Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "reviews": "/api/v1/reviews/{app_id}?app_name={app_name}&limit={limit}",
            "raw_reviews": "/api/v1/reviews/{app_id}/raw?app_name={app_name}&limit={limit}",
            "metrics": "/api/v1/reviews/{app_id}/metrics?app_name={app_name}&limit={limit}"
        },
        "example": {
            "app_name": "nebula-horoscope-astrology",
            "app_id": "1459969523",
            "limit": 100,
            "urls": {
                "reviews": "http://localhost:8001/api/v1/reviews/1459969523?app_name=nebula-horoscope-astrology&limit=100",
                "raw_reviews": "http://localhost:8001/api/v1/reviews/1459969523/raw?app_name=nebula-horoscope-astrology&limit=100",
                "metrics": "http://localhost:8001/api/v1/reviews/1459969523/metrics?app_name=nebula-horoscope-astrology&limit=100"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 