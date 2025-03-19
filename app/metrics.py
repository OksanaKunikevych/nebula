from collections import Counter
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
import logging

from app.utils import clean_text
from app.models import ReviewMetrics

# Configure logging
logger = logging.getLogger(__name__)

def calculate_metrics(reviews: List[Dict[str, Any]]) -> ReviewMetrics:
    """
    Calculate simple metrics from the reviews:
    - Average rating
    - Rating distribution
    - Review length statistics
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        ReviewMetrics object containing calculated metrics
    """
    if not reviews:
        logger.warning("No reviews provided for analysis")
        return ReviewMetrics(
            average_rating=0.0,
            rating_distribution={str(i): 0 for i in range(6)},
            total_reviews=0,
            review_length_stats={"min": 0, "max": 0, "avg": 0}
        )
    
    # Calculate rating metrics
    ratings = [review.get('rating', 0) for review in reviews]
    total_reviews = len(ratings)

    # Calculate average rating
    average_rating = np.mean(ratings) if total_reviews > 0 else 0
    
    # Calculate rating distribution
    rating_counts = Counter(ratings)
    rating_distribution = {
        str(rating): round((rating_counts.get(rating, 0) / total_reviews) * 100, 2)
        for rating in range(6)
    }
    
    # Calculate review length statistics
    review_lengths = [
        len(clean_text(review.get('review_text', ''))) 
        for review in reviews
    ]
    review_length_stats = {
        "min": min(review_lengths),
        "max": max(review_lengths),
        "avg": sum(review_lengths) / total_reviews
    }
    
    return ReviewMetrics(
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        total_reviews=total_reviews,
        review_length_stats=review_length_stats
    )