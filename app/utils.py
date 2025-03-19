from app_store_scraper import AppStore
import random
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import re
from bs4 import BeautifulSoup
from unidecode import unidecode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_app_id(app_id: str) -> None:
    """
    Validate that the app_id is numeric.
    
    Args:
        app_id: The App Store ID to validate
        
    Raises:
        ValueError: If the app_id is not numeric
    """
    if not app_id.isdigit():
        raise ValueError(f"Invalid app_id: {app_id}. App Store ID must be numeric.")

def get_reviews(app_id: str, limit: int = 100, country: str = "us") -> List[Dict[str, Any]]:
    """
    Get reviews from App Store for a specific app.
    
    Args:
        app_id: App Store ID to collect reviews for
        limit: Maximum number of reviews to collect
        country: Country code for the App Store (default: "us")
        
    Returns:
        List of review dictionaries
        
    Raises:
        ValueError: If app_id is not numeric
    """
    try:
        # Validate app_id
        validate_app_id(app_id)
        
        logger.info(f"Initializing AppStore scraper for app id {app_id})")
        app_store = AppStore(country=country, app_name="", app_id=app_id)
        
        logger.info("Starting review collection...")
        # Collect more reviews to ensure we have enough for random selection
        #app_store.review(how_many=limit * 2)
        app_store.review(how_many=limit)
        # Get raw reviews
        raw_reviews = app_store.reviews
        logger.info(f"Found {len(raw_reviews)} total reviews")
        
        # Debug: Print structure of first review
        if raw_reviews:
            logger.info("First review structure:")
            logger.info(raw_reviews[0])
        
        # Randomly select reviews up to the limit
        selected_reviews = random.sample(raw_reviews, min(limit, len(raw_reviews)))
        logger.info(f"Randomly selected {len(selected_reviews)} reviews for analysis")
        
        return selected_reviews[:limit]
    
    except Exception as e:
        logger.error(f"Error collecting reviews: {str(e)}")
        raise

def clean_text(text: str) -> str:
    """
    Clean and normalize text by:
    1. Removing HTML tags
    2. Normalizing Unicode characters
    3. Converting to lowercase
    4. Removing special characters while keeping basic punctuation
    5. Normalizing whitespace
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    try:
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Normalize Unicode characters
        text = unidecode(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        # Normalize whitespace (handle multiple types of whitespace)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    except Exception as e:
        logger.error(f"Error cleaning text: {str(e)}")
        return text

def clean_reviews(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and clean review data.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        List of cleaned review dictionaries
    """
    processed_reviews = []
    
    for review in reviews:
        # Debug: Print raw review before processing
        logger.debug(f"Original title: {review.get('title', '')[:50]}...")
        logger.debug(f"Original review: {review.get('review', '')[:100]}...")
        
        # Skip reviews with empty bodies
        if not review.get('review'):
            logger.info(f"Skipping - empty review")
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
            logger.info(f"Skipping review - empty review after cleaning")
            continue
        
        # Debug: Print processed review
        logger.debug(f"Processed title: {processed_review['title'][:50]}...")
        logger.debug(f"Processed review: {processed_review['review_text'][:100]}...")
        
        processed_reviews.append(processed_review)
    
    logger.info(f"\nProcessed {len(processed_reviews)} reviews (filtered out {len(reviews) - len(processed_reviews)} empty reviews)")
    return processed_reviews