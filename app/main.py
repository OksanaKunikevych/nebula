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
    reviews: List[Review]
    metrics: ReviewMetrics
    insights: InsightAnalysis
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    """
    Root endpoint returning API information and available endpoints.
    """
    return {
        "message": "Welcome to App Store Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "reviews": "/api/v1/reviews/{app_name}?app_id={app_id}&limit={limit}",
            "raw_reviews": "/api/v1/reviews/{app_name}/raw?app_id={app_id}&limit={limit}",
            "metrics": "/api/v1/reviews/{app_name}/metrics?app_id={app_id}&limit={limit}"
        },
        "example": {
            "app_name": "nebula-horoscope-astrology",
            "app_id": "1459969523",
            "limit": 100,
            "urls": {
                "reviews": "http://localhost:8001/api/v1/reviews/nebula-horoscope-astrology?app_id=1459969523&limit=100",
                "raw_reviews": "http://localhost:8001/api/v1/reviews/nebula-horoscope-astrology/raw?app_id=1459969523&limit=100",
                "metrics": "http://localhost:8001/api/v1/reviews/nebula-horoscope-astrology/metrics?app_id=1459969523&limit=100"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 