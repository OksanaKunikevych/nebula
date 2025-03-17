import re
from bs4 import BeautifulSoup
from unidecode import unidecode
from typing import List, Dict, Any

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
        print(f"Error cleaning text: {str(e)}")
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
        print(f"Original review: {review.get('review', '')[:100]}...")
        
        # Skip reviews with empty bodies
        if not review.get('review'):
            print(f"Skipping - empty review")
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
            print(f"Skipping review - empty review after cleaning")
            continue
        
        # Debug: Print processed review
        print(f"Processed review: {processed_review['review_text'][:100]}...")
        
        processed_reviews.append(processed_review)
    
    print(f"\nProcessed {len(processed_reviews)} reviews (filtered out {len(reviews) - len(processed_reviews)} empty reviews)")
    return processed_reviews 