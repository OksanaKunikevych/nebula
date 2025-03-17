from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import io

from app.utils import get_reviews, clean_reviews
from app.metrics import calculate_metrics
from app.nlp_analysis import analyze_reviews

router = APIRouter()

@router.get("/reviews/{app_name}")
async def collect_reviews(
    app_name: str,
    app_id: str = Query(..., description="App Store ID of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Collect and process reviews for a specific app.
    """
    try:
        # Get raw reviews
        raw_reviews = get_reviews(app_name, app_id, limit)
        
        # Clean and process reviews
        processed_reviews = clean_reviews(raw_reviews)
        
        return {
            "status": "success",
            "message": f"Successfully collected and processed {len(processed_reviews)} reviews",
            "data": processed_reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_name}/raw")
async def get_raw_reviews(
    app_name: str,
    app_id: str = Query(..., description="App Store ID of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Get raw reviews for a specific app.
    """
    try:
        raw_reviews = get_reviews(app_name, app_id, limit)
        return {
            "status": "success",
            "message": f"Successfully collected {len(raw_reviews)} raw reviews",
            "data": raw_reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_name}/metrics")
async def get_app_metrics(
    app_name: str,
    app_id: str = Query(..., description="App Store ID of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Get metrics for a specific app's reviews.
    """
    try:
        # Get raw reviews
        raw_reviews = get_reviews(app_name, app_id, limit)
        
        # Clean and process reviews
        processed_reviews = clean_reviews(raw_reviews)
        
        # Calculate metrics
        metrics = calculate_metrics(processed_reviews)
        
        return {
            "status": "success",
            "message": f"Successfully calculated metrics for {len(processed_reviews)} reviews",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 