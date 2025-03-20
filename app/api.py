from asyncio.log import logger
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import json
import io
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
import os

from .metrics import calculate_metrics
from .utils import get_reviews, clean_reviews, validate_app_id
from .database import Database
from .models import (
    RawReview, ProcessedReview, ReviewMetrics,
    InsightsMetrics, MetricsResponse, ReviewResponse, RawReviewResponse
)
from .nlp_analysis import nlp_analyze_reviews, get_sentiment

router = APIRouter()

# Initialize database
try:
    db = Database("mongodb://localhost:27017")
except ConnectionError as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    db = None

@router.get("/wordcloud/{app_id}")
async def get_wordcloud(app_id: str):
    """
    Get the wordcloud image for a specific app.
    """
    try:
        wordcloud_path = Path("static/wordclouds") / f"wordcloud_{app_id}.png"
        if not wordcloud_path.exists():
            logger.error(f"Wordcloud not found at path: {wordcloud_path}")
            raise HTTPException(status_code=404, detail="Wordcloud not found")
        
        # Log the file path for debugging
        logger.info(f"Serving wordcloud from: {wordcloud_path}")
        
        return FileResponse(
            wordcloud_path,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except Exception as e:
        logger.error(f"Error serving wordcloud: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reviews/{app_id}")
async def collect_reviews(
    app_id: str,
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Collect and process reviews for a specific app.
    """
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service is unavailable. Please try again later."
            )
            
        # Validate app_id
        validate_app_id(app_id)
        
        # Get raw reviews
        raw_reviews = get_reviews(app_id, limit)
        
        # Save raw reviews
        raw_count = await db.save_raw_reviews(app_id, raw_reviews)
        
        # Clean and process reviews
        processed_reviews = clean_reviews(raw_reviews)
        
        # Add sentiment analysis to processed reviews
        for review in processed_reviews:
            sentiment, score = get_sentiment(review['review_text'])
            review['sentiment'] = sentiment
            review['sentiment_score'] = score
            review['date_processed'] = datetime.utcnow()
        
        # Save processed reviews
        processed_count = await db.save_processed_reviews(app_id, processed_reviews)
        
        # Calculate metrics
        metrics = calculate_metrics(processed_reviews)
        
        # Perform NLP analysis
        insights = nlp_analyze_reviews(processed_reviews, app_id)
        
        # Save metrics and insights
        await db.save_metrics(app_id, metrics)
        await db.save_insights(app_id, insights)
        
        return {
            "status": "success",
            "message": f"Successfully collected and processed {processed_count} reviews",
            "data": {
                "raw_reviews_count": raw_count,
                "processed_reviews_count": processed_count,
                "metrics": metrics.dict(),
                "insights": insights.dict()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_id}/raw")
async def get_raw_reviews(
    app_id: str,
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Get raw reviews for a specific app.
    """
    try:
        # Validate app_id
        validate_app_id(app_id)
        
        # Get raw reviews from database
        reviews = await db.get_raw_reviews(app_id, limit)

        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this app")
        
        # Convert to JSON string
        json_data = json.dumps({
            "app_id": app_id,
            "reviews": reviews
        }, indent=2, default=str)
        
        # Create a streaming response
        return StreamingResponse(
            io.StringIO(json_data),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={app_id}_raw_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_id}/metrics", response_model=MetricsResponse)
async def get_app_metrics(
    app_id: str
):
    """
    Get metrics and insights for a specific app's reviews.
    """
    try:
        # Validate app_id
        validate_app_id(app_id)
        
        # Get metrics from database
        metrics_data = await db.get_metrics(app_id)
        
        # Get insights from database
        insights_data = await db.get_insights(app_id)
        
        if not metrics_data:
            raise HTTPException(status_code=404, detail="No metrics found for this app")
        
        # Convert database data to Pydantic models
        metrics = ReviewMetrics(**metrics_data)
        insights = InsightsMetrics(**insights_data)
        
        return MetricsResponse(
            status="success",
            message="Successfully retrieved metrics and insights",
            data={
                "metrics": metrics.dict(),
                "insights": insights.dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 