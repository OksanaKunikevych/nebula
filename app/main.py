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
    review_id: str
    rating: int
    title: Optional[str]
    body: str
    date: datetime
    developer_response: Optional[str]
    developer_response_date: Optional[datetime]
    processed: bool = False

class ReviewResponse(BaseModel):
    reviews: List[Review]
    metrics: ReviewMetrics
    insights: InsightAnalysis
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
    Collect latest reviews for a specified app and analyze them.
    
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
        app_store.review(how_many=limit * 2)  # Collect more reviews to ensure we have enough
        
        if not app_store.reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for app_id: {app_id}"
            )
        
        logger.info(f"Found {len(app_store.reviews)} total reviews")
        
        # Debug: Print raw review data
        if app_store.reviews:
            first_review = app_store.reviews[0]
            logger.info("Sample raw review data:")
            logger.info(f"Review ID: {first_review.get('review_id')}")
            logger.info(f"Rating: {first_review.get('rating')}")
            logger.info(f"Title: {first_review.get('title')}")
            logger.info(f"Body: {first_review.get('body')}")
            logger.info(f"Date: {first_review.get('date')}")
            logger.info(f"Developer Response: {first_review.get('developer_response')}")
            logger.info(f"Developer Response Date: {first_review.get('developer_response_date')}")
        
        # Sort reviews by date (newest first) and select the latest ones
        sorted_reviews = sorted(
            app_store.reviews,
            key=lambda x: x.get('date', datetime.min),
            reverse=True
        )
        selected_reviews = sorted_reviews[:limit]
        logger.info(f"Selected {len(selected_reviews)} latest reviews for analysis")
        
        # Debug: Print selected review data
        if selected_reviews:
            first_selected = selected_reviews[0]
            logger.info("Sample selected review data:")
            logger.info(f"Review ID: {first_selected.get('review_id')}")
            logger.info(f"Rating: {first_selected.get('rating')}")
            logger.info(f"Title: {first_selected.get('title')}")
            logger.info(f"Body: {first_selected.get('body')}")
            logger.info(f"Date: {first_selected.get('date')}")
            logger.info(f"Developer Response: {first_selected.get('developer_response')}")
            logger.info(f"Developer Response Date: {first_selected.get('developer_response_date')}")

        # Process and clean the reviews
        processed_reviews = process_reviews(selected_reviews)
        logger.info(f"Processed {len(processed_reviews)} reviews")
        
        # Debug: Print processed review data
        if processed_reviews:
            first_processed = processed_reviews[0]
            logger.info("Sample processed review data:")
            logger.info(f"Review ID: {first_processed.get('review_id')}")
            logger.info(f"Rating: {first_processed.get('rating')}")
            logger.info(f"Title: {first_processed.get('title')}")
            logger.info(f"Body: {first_processed.get('body')}")
            logger.info(f"Date: {first_processed.get('date')}")
            logger.info(f"Developer Response: {first_processed.get('developer_response')}")
            logger.info(f"Developer Response Date: {first_processed.get('developer_response_date')}")
            logger.info(f"Processed: {first_processed.get('processed')}")
        
        # Calculate metrics
        metrics = calculate_metrics(selected_reviews)
        logger.info("Calculated metrics")
        
        # Perform NLP analysis
        logger.info("Starting NLP analysis...")
        insights = analyze_reviews(selected_reviews)
        logger.info("Completed NLP analysis")
        
        # Calculate metadata
        execution_time = time.time() - start_time
        metadata = {
            "total_reviews_collected": len(app_store.reviews),
            "reviews_returned": len(processed_reviews),
            "execution_time_seconds": round(execution_time, 2),
            "country": country,
            "app_id": app_id,
            "app_name": app_name,
            "date_range": {
                "latest_review": selected_reviews[0].get('date').isoformat() if selected_reviews else None,
                "oldest_review": selected_reviews[-1].get('date').isoformat() if selected_reviews else None
            }
        }
        
        return ReviewResponse(
            reviews=processed_reviews,
            metrics=metrics,
            insights=insights,
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