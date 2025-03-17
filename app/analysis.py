from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
import re
from pydantic import BaseModel
from bs4 import BeautifulSoup
from unidecode import unidecode
import numpy as np

class ReviewMetrics(BaseModel):
    average_rating: float
    rating_distribution: Dict[int, float]  # rating -> percentage
    total_reviews: int
    review_length_stats: Dict[str, float]  # min, max, avg length

def clean_text(text: str) -> str:
    """
    Clean and preprocess review text.
    
    Args:
        text: Raw review text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Debug: Print original text
    print(f"Original text: {text[:100]}...")
    
    # 1. Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # 2. Normalize Unicode characters
    text = unidecode(text)
    
    # 3. Convert to lowercase
    text = text.lower()
    
    # 4. Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?]', ' ', text)
    
    # 5. Normalize whitespace (spaces, tabs, line breaks)
    text = re.sub(r'\s+', ' ', text)
    
    # 6. Remove leading/trailing whitespace
    text = text.strip()
    
    # Debug: Print cleaned text
    print(f"Cleaned text: {text[:100]}...")
    
    return text

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

def process_reviews(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and clean review data.
    
    Args:
        reviews: List of raw review dictionaries
        
    Returns:
        List of processed review dictionaries
    """
    processed_reviews = []
    
    for review in reviews:
        # Debug: Print raw review before processing
        print(f"\nProcessing review {review.get('review_id')}:")
        print(f"Original review: {review.get('review', '')[:100]}...")
        
        # Skip reviews with empty bodies
        if not review.get('review'):
            print(f"Skipping review {review.get('review_id')} - empty review")
            continue
        
        processed_review = {
            'rating': review.get('rating', 0),
            'title': clean_text(review.get('title', '')),
            'review_text': clean_text(review.get('review', '')),
            'date': review.get('date'),
            'processed': True
        }
        
        # Skip if cleaning resulted in empty review_text
        if not processed_review['review_text']:
            print(f"Skipping review {review.get('review_id')} - empty review after cleaning")
            continue
        
        # Debug: Print processed review
        print(f"Processed review: {processed_review['review_text'][:100]}...")
        
        processed_reviews.append(processed_review)
    
    print(f"\nProcessed {len(processed_reviews)} reviews (filtered out {len(reviews) - len(processed_reviews)} empty reviews)")
    return processed_reviews 