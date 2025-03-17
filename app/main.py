from fastapi import FastAPI, HTTPException, Query
from app_store_scraper import AppStore
from typing import List, Optional
import random
from pydantic import BaseModel
from datetime import datetime
import logging
import time
from typing import Dict, Any
from .analysis import process_reviews, calculate_metrics, ReviewMetrics
from .nlp_analysis import analyze_reviews, InsightAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Apple Store Review Analysis API",
    description="API for collecting and analyzing App Store reviews",
    version="1.0.0"
)

class Review(BaseModel):
    rating: int
    title: Optional[str]
    review_text: str
    date: datetime
    processed: bool = False

class ReviewResponse(BaseModel):
    reviews: List[Review]
    # metrics: ReviewMetrics
    # insights: InsightAnalysis
    metadata: Dict[str, Any]

def validate_app_id(app_id: str) -> bool:
    """Validate that the app_id is a valid Apple Store ID."""
    try:
        # Apple Store IDs are typically numeric
        int(app_id)
        return True
    except ValueError:
        return False

@app.get("/reviews/{app_id}", response_model=ReviewResponse)
async def get_reviews(
    app_id: str,
    app_name: str = Query(..., description="Name of the app in App Store"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of reviews to collect"),
    country: str = Query(default="us", description="Country code for App Store")
):
    """
    Collect random reviews for a specified app and analyze them.
    
    Args:
        app_id: The App Store ID of the application
        app_name: Name of the app in App Store
        limit: Number of reviews to collect (default: 100, max: 1000)
        country: Country code for App Store (default: us)
    
    Returns:
        List of processed reviews with metrics, insights, and metadata
    """
    start_time = time.time()
    
    try:
        # Validate app_id
        if not validate_app_id(app_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid app_id format. App Store IDs should be numeric."
            )

        # Initialize the AppStore scraper
        logger.info(f"Initializing AppStore scraper for app_id: {app_id}, app_name: {app_name}")
        app_store = AppStore(country=country, app_id=app_id, app_name=app_name)
        
        # Collect reviews with rate limiting
        logger.info(f"Collecting reviews for app_id: {app_id}")
        app_store.review(how_many=limit * 2)  # Collect more reviews to ensure we have enough for random selection after cleaning
        
        if not app_store.reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for app_id: {app_id}"
            )
        logger.info(f"Found {len(app_store.reviews)} total reviews")
        
        # Randomly select reviews up to the limit
        selected_reviews = random.sample(app_store.reviews, min(limit, len(app_store.reviews)))
        
        # Sort by date:
        # sorted_reviews = sorted(
        #     app_store.reviews,
        #     key=lambda x: x.get('date', datetime.min),
        #     reverse=True
        # )
        # selected_reviews = sorted_reviews[:limit]
        
        logger.info(f"Selected {len(selected_reviews)} random reviews for analysis")
        
        # Process and clean the reviews
        processed_reviews = process_reviews(selected_reviews)
        
        # Calculate metrics
        #metrics = calculate_metrics(selected_reviews)
        
        # Perform NLP analysis
        #insights = analyze_reviews(selected_reviews)
        
        # Calculate metadata
        execution_time = time.time() - start_time
        metadata = {
            "total_reviews_collected": len(app_store.reviews),
            "reviews_returned": len(processed_reviews),
            "execution_time_seconds": round(execution_time, 2),
            "country": country,
            "app_id": app_id,
            "app_name": app_name
        }
        
        return ReviewResponse(
            reviews=processed_reviews,
            #metrics=metrics,
            #insights=insights,
            metadata=metadata
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error collecting reviews: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error collecting reviews: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to Apple Store Review Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "reviews": "/reviews/{app_id}",
            "docs": "/docs"
        }
    } 