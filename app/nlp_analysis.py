from typing import List, Dict, Any, Tuple
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
    semantic_keywords: List[Dict[str, Any]]  # list of {keyword: score} for most important keywords
    negative_keywords: List[Dict[str, Any]]  # list of {keyword: score} for negative reviews
    key_phrases: List[str]  # important phrases extracted from reviews

class InsightAnalysis(BaseModel):
    sentiment: SentimentAnalysis
    keywords: KeywordAnalysis
    improvement_areas: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "sentiment": {
                    "overall_sentiment": "POSITIVE",
                    "sentiment_score": 0.75,
                    "sentiment_distribution": {
                        "POSITIVE": 70,
                        "NEGATIVE": 20,
                        "NEUTRAL": 10
                    },
                },
                "keywords": {
                    "semantic_keywords": [
                        {"keyword": "accurate", "score": 0.8},
                        {"keyword": "user-friendly", "score": 0.7}
                    ],
                    "negative_keywords": [
                        {"keyword": "crash", "score": 0.6},
                        {"keyword": "slow", "score": 0.5}
                    ],
                    "key_phrases": []
                },
                "improvement_areas": [
                    "Address issues related to 'crash'",
                    "Address issues related to 'slow'"
                ]
            }
        }

def get_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyze sentiment of text using transformers pipeline.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (sentiment, score)
    """
    if not text:
        return "NEUTRAL", 0.0
    
    try:
        # Get sentiment analysis result
        result = sentiment_analyzer(text[:512])[0]  # Limit text length to 512 tokens for better performance
        
        # Use native transformer labels (POSITIVE/NEGATIVE)
        sentiment = result['label']
        score = result['score']
        
        print(f"Sentiment analysis for text: '{text[:50]}...' - Sentiment: {sentiment}, Score: {score}")
        
        return sentiment, score
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return "NEUTRAL", 0.0

def extract_keywords(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extract semantic keywords using KeyBERT.
    
    Args:
        text: Text to analyze
        top_n: Number of keywords to extract
        
    Returns:
        List of dictionaries containing keywords and their scores
    """
    if not text:
        return []
    
    try:
        # Extract keywords with KeyBERT
        # TODO: try with other embedding models: https://github.com/MaartenGr/KeyBERT
        keywords = keybert_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),  # Extract single words and phrases up to 3 words
            stop_words='english',
            top_n=top_n
        )
        
        # Convert to list of dictionaries
        return [
            {"keyword": keyword, "score": score}
            for keyword, score in keywords
        ]
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
                sentiment_distribution={"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            ),
            keywords=KeywordAnalysis(
                semantic_keywords=[],
                negative_keywords=[],
                key_phrases=[]
            ),
            improvement_areas=[]
        )
    
    logger.info(f"Analyzing {len(reviews)} reviews")
    
    # Separate negative reviews (rating <= 2)
    negative_reviews = [
        review for review in reviews
        if review.get('rating', 0) <= 2
    ]
    
    # Combine all review texts
    all_text = " ".join(review.get('review_text', '') for review in reviews)
    negative_text = " ".join(
        review.get('review_text', '')
        for review in negative_reviews
    )
    
    logger.info(f"Combined text length: {len(all_text)}")
    logger.info(f"Negative reviews count: {len(negative_reviews)}")
    
    # Sentiment Analysis
    sentiments = []
    scores = []
    
    for review in reviews:
        sentiment, score = get_sentiment(review.get('review_text', ''))
        sentiments.append(sentiment)
        scores.append(score)
        print(f"--------------------------------")
        print(f"Review: {review.get('review_text')}")
        print(f"Rating: {review.get('rating')}")
        print('\n')
        print(f"Sentiment: {sentiment}")
        print(f"Score: {score}")
        print(f"--------------------------------")
        # Get sentiment scores from processed reviews
    sentiment_scores = [review.get('sentiment_score', 0) for review in reviews]
    sentiments = [review.get('sentiment', 'NEUTRAL') for review in reviews]
    # Calculate overall sentiment based on normalized scores
    normalized_scores = []
    for sentiment, score in zip(sentiments, sentiment_scores):
        if sentiment == "POSITIVE":
            normalized_scores.append(score)
        else:  # NEGATIVE
            normalized_scores.append(-score)
    
    avg_score = sum(normalized_scores) / len(normalized_scores)
    normalized_avg = (avg_score + 1) / 2
    
    # Determine overall sentiment with granular labels
    if normalized_avg > 0.9:
        overall_sentiment = "VERY_POSITIVE"
    elif normalized_avg > 0.7:
        overall_sentiment = "POSITIVE"
    elif normalized_avg > 0.5:
        overall_sentiment = "SLIGHTLY_POSITIVE"
    elif normalized_avg == 0.5:
        overall_sentiment = "NEUTRAL"
    elif normalized_avg > 0.3:
        overall_sentiment = "SLIGHTLY_NEGATIVE"
    elif normalized_avg > 0.1:
        overall_sentiment = "NEGATIVE"
    else:
        overall_sentiment = "VERY_NEGATIVE"

    # Calculate sentiment distribution
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)
    sentiment_distribution = {
        sentiment: count  # Use raw count instead of percentage
        for sentiment, count in sentiment_counts.items()
    }
    
    # Keyword Analysis
    logger.info("Starting keyword analysis...")
    semantic_keywords = extract_keywords(all_text)
    
    # Negative keywords analysis
    logger.info("Starting negative keyword analysis...")
    negative_keywords = extract_keywords(negative_text)
    
    # Generate Insights
    improvement_areas = []
    
    # Analyze negative keywords for improvement areas
    for keyword in negative_keywords:
        if keyword['score'] > 0.3:  # Only consider significant keywords
            improvement_areas.append(f"Address issues related to '{keyword['keyword']}'")
    
    logger.info(f"Found {len(improvement_areas)} improvement areas")
    
    return InsightAnalysis(
        sentiment=SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=round(normalized_avg, 2),
            sentiment_distribution=sentiment_distribution
        ),
        keywords=KeywordAnalysis(
            semantic_keywords=semantic_keywords,
            negative_keywords=negative_keywords,
            key_phrases=[]  # TODO: add key phrases extraction
        ),
        improvement_areas=improvement_areas
    ) 