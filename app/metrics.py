from collections import Counter
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from pydantic import BaseModel

from app.data_cleaning import clean_text

class ReviewMetrics(BaseModel):
    average_rating: float
    rating_distribution: Dict[int, float]  # rating -> percentage
    total_reviews: int
    review_length_stats: Dict[str, float]  # min, max, avg length

def calculate_metrics(reviews: List[Dict[str, Any]]) -> ReviewMetrics:
    """
    Calculate averae rating and rating distribution metrics from the reviews.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        ReviewMetrics object containing calculated metrics
    """
    if not reviews:
        logger.warning("No reviews provided for analysis")
        return ReviewMetrics(
            average_rating=0.0,
            rating_distribution={i: 0.0 for i in range(6)},  # Initialize all ratings from 0 to 5
            total_reviews=0,
            review_length_stats={"min": 0, "max": 0, "avg": 0},
        )
    
    # Calculate rating metrics
    ratings = [review.get('rating', 0) for review in reviews]
    total_reviews = len(ratings)

    # Calculate average rating
    average_rating = np.mean(ratings) if total_reviews > 0 else 0
    
    # Calculate rating distribution
    rating_counts = Counter(ratings)
    rating_distribution = {
        rating: (rating_counts.get(rating, 0) / total_reviews) * 100 
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
        review_length_stats=review_length_stats,
    )