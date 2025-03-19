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
            rating_distribution={str(i): 0 for i in range(6)},
            total_reviews=0,
            review_length_stats={"min": 0, "max": 0, "avg": 0},
            overall_sentiment="N/A",
            overall_sentiment_score=0.0,
            sentiment_distribution={"POSITIVE": 0, "NEGATIVE": 0}
        )
    
    # Calculate rating metrics
    ratings = [review.get('rating', 0) for review in reviews]
    total_reviews = len(ratings)

    # Calculate average rating
    average_rating = np.mean(ratings) if total_reviews > 0 else 0
    
    # Calculate rating distribution
    rating_counts = Counter(ratings)
    rating_distribution = {
        str(rating): rating_counts.get(rating, 0)
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

    # Calculate sentiment metrics
    sentiments = [review.get('sentiment', 'POSITIVE') for review in reviews]
    sentiment_scores = [review.get('sentiment_score', 0.0) for review in reviews]
    
    # Calculate sentiment distribution
    sentiment_counts = Counter(sentiments)
    sentiment_distribution = {
        "POSITIVE": sentiment_counts.get("POSITIVE", 0),
        "NEGATIVE": sentiment_counts.get("NEGATIVE", 0)
    }
    
    # Calculate average sentiment score
    overall_sentiment_score = np.mean(sentiment_scores) if sentiment_scores else 0.0
    
    # Determine overall sentiment based on distribution
    positive_count = sentiment_distribution.get("POSITIVE", 0)
    negative_count = sentiment_distribution.get("NEGATIVE", 0)
    
    if positive_count > negative_count:
        overall_sentiment = "VERY_POSITIVE" if overall_sentiment_score > 0.8 else "POSITIVE"
    elif negative_count > positive_count:
        overall_sentiment = "VERY_NEGATIVE" if overall_sentiment_score < -0.8 else "NEGATIVE"
    else:
        # Map scores to sentiment categories based on magnitude and sign
        score_magnitude = abs(overall_sentiment_score)
        if score_magnitude > 0.8:
            overall_sentiment = "VERY_" + ("POSITIVE" if overall_sentiment_score > 0 else "NEGATIVE")
        elif score_magnitude > 0.6:
            overall_sentiment = "POSITIVE" if overall_sentiment_score > 0 else "NEGATIVE"
        else:
            overall_sentiment = "SLIGHTLY_" + ("POSITIVE" if overall_sentiment_score > 0 else "NEGATIVE")
    
    return ReviewMetrics(
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        total_reviews=total_reviews,
        review_length_stats=review_length_stats,
        overall_sentiment=overall_sentiment,
        overall_sentiment_score=round(overall_sentiment_score, 2),
        sentiment_distribution=sentiment_distribution
    )