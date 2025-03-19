from typing import List, Dict, Any, Tuple, Optional
from textblob import TextBlob
from collections import Counter
from pydantic import BaseModel, Field
import nltk
from nltk.corpus import stopwords
from transformers import pipeline
from keybert import KeyBERT
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('stopwords')
    print("NLTK data download complete.")

# Get stopwords
STOPWORDS = set(stopwords.words('english'))
# TODO: Add custom stopwords
# TODO: Get stopwords from Bert instead

# Initialize sentiment analyzer
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1  # Use CPU for better compatibility
)

# Initialize KeyBERT for keyword extraction
keybert_model = KeyBERT()

class SentimentAnalysis(BaseModel):
    overall_sentiment: str
    sentiment_score: float
    sentiment_distribution: Dict[str, int]

class KeywordAnalysis(BaseModel):
    negative_keywords: List[str]  # list of keywords from negative reviews


class InsightAnalysis(BaseModel):
    sentiment: SentimentAnalysis
    keywords: KeywordAnalysis
    improvement_areas: List[str] = Field(default_factory=list)

def get_sentiment(text: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Analyze sentiment of text using transformers pipeline.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (sentiment, score) or (None, None) if text is empty
    """
    if not text:
        logger.warning("No text provided for sentiment analysis!")
        return None, None
    
    try:
        # Get sentiment analysis result
        result = sentiment_analyzer(text[:512])[0]  # Limit text length to 512 tokens for better performance
        
        # Extract only the fields we need
        sentiment = result.get('label', 'N/A')  # Default to N/A if label is missing
        score = result.get('score', 0.0)
        
        # Convert score to -1 to 1 range for consistency
        if sentiment == "NEGATIVE":
            score = -score

        print(f"Sentiment analysis for text: '{text[:50]}...' - Sentiment: {sentiment}, Score: {score}")
        
        return sentiment, score
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return None, None

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract semantic keywords using KeyBERT.
    
    Args:
        text: Text to analyze
        top_n: Number of keywords to extract
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    try:
        # Extract keywords with KeyBERT
        # TODO: try with other embedding models: https://github.com/MaartenGr/KeyBERT
        keywords = keybert_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3), # Extract single words and phrases up to 3 words
            stop_words='english',
            top_n=top_n,
            use_mmr=True, # ensures that keywords are not too similar
            #diversity=0.7 # diversity of keywords
        )
        return [keyword for keyword, _ in keywords]
    
    except Exception as e:
        logger.error(f"Error in keyword extraction: {str(e)}")
        return []


def nlp_analyze_reviews(reviews: List[Dict[str, Any]]) -> InsightAnalysis:
    """
    Perform comprehensive NLP analysis on reviews.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        InsightAnalysis object with sentiment, keywords, and insights
    """
    if not reviews:
        logger.info("No reviews to analyze")
        return InsightAnalysis(
            sentiment=SentimentAnalysis(
                overall_sentiment="NEUTRAL",
                sentiment_score=0.0,
                sentiment_distribution={"POSITIVE": 0, "NEGATIVE": 0}
            ),
            keywords=KeywordAnalysis(
                negative_keywords=[]
            ),
            improvement_areas=[]
        )
    
    logger.info(f"Analyzing {len(reviews)} reviews")
    
    # Sentiment Analysis
    sentiments = []
    scores = []
    
    for review in reviews:
        # Combine title and review text for sentiment analysis
        combined_text = f"{review.get('title', '')} {review.get('review_text', '')}"
        sentiment, score = get_sentiment(combined_text)
        
        # Skip if sentiment analysis failed
        if sentiment is None or score is None:
            logger.warning(f"Sentiment analysis failed for review: {review}")
            continue
            
        sentiments.append(sentiment)
        scores.append(score)
        print(f"--------------------------------")
        print(f"Combined text: {combined_text}")
        print(f"Rating: {review.get('rating')}")
        print('\n')
        print(f"Sentiment: {sentiment}")
        print(f"Score: {score}")
        print(f"--------------------------------")
    
    # If no valid sentiments were found, return neutral analysis
    if not sentiments:
        return InsightAnalysis(
            sentiment=SentimentAnalysis(
                overall_sentiment="N/A",
                sentiment_score=0.0,
                sentiment_distribution={"POSITIVE": 0, "NEGATIVE": 0}
            ),
            keywords=KeywordAnalysis(
                negative_keywords=[]
            ),
            improvement_areas=[]
        )
    
    # Calculate sentiment distribution
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)
    sentiment_distribution = {
        "POSITIVE": sentiment_counts.get("POSITIVE", 0),
        "NEGATIVE": sentiment_counts.get("NEGATIVE", 0)
    }
    
    # Calculate average sentiment score (-1 to 1 scale)
    if len(scores) > 0:
        avg_score = sum(scores) / len(scores)
    else:
        logger.warning("No valid sentiments found for sentiment analysis")
        avg_score = 0.0
        
    # Determine overall sentiment based on distribution
    positive_count = sentiment_distribution.get("POSITIVE", 0)
    negative_count = sentiment_distribution.get("NEGATIVE", 0)
    
    # If there's a clear majority in the distribution, use that
    if positive_count > negative_count:
        overall_sentiment = "VERY_POSITIVE" if avg_score > 0.8 else "POSITIVE"
    elif negative_count > positive_count:
        overall_sentiment = "VERY_NEGATIVE" if avg_score < -0.8 else "NEGATIVE"
    else:
        # Map scores to sentiment categories based on magnitude and sign
        score_magnitude = abs(avg_score)
        if score_magnitude > 0.8:
            overall_sentiment = "VERY_" + ("POSITIVE" if avg_score > 0 else "NEGATIVE")
        elif score_magnitude > 0.6:
            overall_sentiment = "POSITIVE" if avg_score > 0 else "NEGATIVE"
        else:
            overall_sentiment = "SLIGHTLY_" + ("POSITIVE" if avg_score > 0 else "NEGATIVE")

    # Keyword Analysis
    logger.info("Starting keyword analysis...")
    
    # Filter out negative reviews
    negative_reviews = [review for review in reviews if review.get('rating', 0) <= 2]
    negative_text = " ".join(review.get('review_text', '') for review in negative_reviews)
    # Extract keywords from combined negative reviews
    negative_keywords = extract_keywords(negative_text)
    
    print(">>>>>>>>>>>>>>>>>")
    print(f"Negative keywords: {negative_keywords}")
    print(">>>>>>>>>>>>>>>>>")

    
    # Generate improvement areas from negative keywords
    improvement_areas = [f"Address issues related to '{keyword}'" for keyword in negative_keywords]
    
    logger.info(f"Generated {len(improvement_areas)} improvement areas")
    
    return InsightAnalysis(
        sentiment=SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=round(avg_score, 2),
            sentiment_distribution=sentiment_distribution
        ),
        keywords=KeywordAnalysis(
            negative_keywords=negative_keywords,
        ),
        improvement_areas=improvement_areas
    ) 