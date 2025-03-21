from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from pathlib import Path

from app.utils import clean_reviews
from app.models import ProcessedReview, ReviewResponse, RawReviewResponse, MetricsResponse
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

# Mount static files directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Root endpoint returning API information and available endpoints.
    """
    return {
        "message": "Welcome to App Store Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "collect_reviews": {
                "method": "POST",
                "path": "/api/v1/reviews/{app_id}",
                "description": "Scrapes, stores, and processes reviews for the specified app",
                "parameters": {
                    "app_id": "Required. App Store ID of the app",
                    "limit": "Optional. Maximum number of reviews to collect (default: 100)"
                }
            },
            "get_raw_reviews": {
                "method": "GET",
                "path": "/api/v1/reviews/{app_id}/raw",
                "description": "Retrieves raw review data",
                "parameters": {
                    "app_id": "Required. App Store ID of the app",
                    "limit": "Optional. Number of reviews to return (default: 100)"
                }
            },
            "get_metrics": {
                "method": "GET",
                "path": "/api/v1/reviews/{app_id}/metrics",
                "description": "Retrieves aggregated insights from processed reviews",
                "parameters": {
                    "app_id": "Required. App Store ID of the app"
                }
            }
        },
        "example": {
            "app_id": "1459969523",
            "limit": 100,
            "urls": {
                "collect_reviews": "curl -X POST 'http://localhost:8001/api/v1/reviews/1459969523?limit=100'",
                "raw_reviews": "http://localhost:8001/api/v1/reviews/1459969523/raw?limit=100'",
                "metrics": "http://localhost:8001/api/v1/reviews/1459969523/metrics'"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 