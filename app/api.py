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

@router.get("/reviews/{app_id}")
async def collect_reviews(
    app_id: str,
    app_name: Optional[str] = Query(None, description="Optional name of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Collect and process reviews for a specific app.
    """
    try:
        # Get raw reviews
        raw_reviews = get_reviews(app_name or "", app_id, limit)
        
        # Clean and process reviews
        processed_reviews = clean_reviews(raw_reviews)
        
        return {
            "status": "success",
            "message": f"Successfully collected and processed {len(processed_reviews)} reviews",
            "data": processed_reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_id}/raw")
async def get_raw_reviews(
    app_id: str,
    app_name: Optional[str] = Query(None, description="Optional name of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Get raw reviews for a specific app.
    """
    try:
        raw_reviews = get_reviews(app_name, app_id, limit)

        if not raw_reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this app. Please make sure the app ID is correct.")
        
        # Convert reviews to JSON string
        json_data = json.dumps(raw_reviews, indent=2, default=str)
        # Create a streaming response
        return StreamingResponse(
            io.StringIO(json_data),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={app_name or app_id}_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{app_id}/metrics")
async def get_app_metrics(
    app_id: str,
    app_name: Optional[str] = Query(None, description="Optional name of the app"),
    limit: int = Query(100, description="Maximum number of reviews to collect")
):
    """
    Get metrics for a specific app's reviews.
    """
    try:
        # Get raw reviews
        raw_reviews = get_reviews(app_name or "", app_id, limit)
        
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