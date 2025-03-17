from typing import List, Dict, Any, Tuple
from textblob import TextBlob
from collections import Counter
from pydantic import BaseModel
import nltk
from nltk.corpus import stopwords
from transformers import pipeline

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

class SentimentAnalysis(BaseModel):
    overall_sentiment: str  # POSITIVE, NEGATIVE, or NEUTRAL
    sentiment_score: float  # 0 to 1
    sentiment_distribution: Dict[str, float]  # percentage of each sentiment
    confidence: float  # confidence in the sentiment analysis

class KeywordAnalysis(BaseModel):
    common_keywords: List[Dict[str, Any]]  # list of {word: count} for most common words
    negative_keywords: List[Dict[str, Any]]  # list of {word: count} for negative reviews
    key_phrases: List[str]  # important phrases extracted from reviews

class InsightAnalysis(BaseModel):
    sentiment: SentimentAnalysis
    # keywords: KeywordAnalysis
    # improvement_areas: List[str]  # suggested areas for improvement
    # strengths: List[str]  # identified strengths
    # weaknesses: List[str]  # identified weaknesses

def get_sentiment(text: str) -> Tuple[str, float, float]:
    """
    Analyze sentiment of text using transformers pipeline.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (sentiment, score, confidence)
    """
    if not text:
        return "NEUTRAL", 0.0, 0.0
    
    try:
        # Get sentiment analysis result
        result = sentiment_analyzer(text[:512])[0]  # Limit text length to 512 tokens
        
        # Use native transformer labels (POSITIVE/NEGATIVE)
        sentiment = result['label']
        score = result['score']
        confidence = result['score']
        
        print(f"Sentiment analysis for text: '{text[:50]}...' - Sentiment: {sentiment}, Score: {score}, Confidence: {confidence}")
        
        return sentiment, score, confidence
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "NEUTRAL", 0.0, 0.0

def extract_keywords(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extract important keywords from text using TextBlob.
    
    Args:
        text: Text to analyze
        top_n: Number of top keywords to return
        
    Returns:
        List of dictionaries with word and count
    """
    if not text:
        return []
    
    try:
        # Use TextBlob for tokenization and part-of-speech tagging
        blob = TextBlob(text.lower())
        
        # Get words and their parts of speech, excluding stopwords
        words = [word for word, tag in blob.tags 
                if tag.startswith(('NN', 'JJ', 'VB'))  # Nouns, adjectives, verbs
                and len(word) > 2
                and word not in STOPWORDS]  # Exclude stopwords
        
        # Count frequencies
        word_freq = Counter(words)
        
        # Return top N keywords
        result = [
            {"word": word, "count": count}
            for word, count in word_freq.most_common(top_n)
        ]
        print(f"Extracted keywords: {result}")
        return result
    except Exception as e:
        print(f"Error in keyword extraction: {str(e)}")
        return []

def extract_key_phrases(text: str, top_n: int = 5) -> List[str]:
    """
    Extract important phrases from text using TextBlob.
    
    Args:
        text: Text to analyze
        top_n: Number of top phrases to return
        
    Returns:
        List of important phrases
    """
    if not text:
        return []
    
    try:
        # Use TextBlob for noun phrases
        blob = TextBlob(text)
        phrases = blob.noun_phrases
        
        # Filter and sort phrases
        filtered_phrases = [
            phrase for phrase in phrases
            if len(phrase.split()) >= 4  # Only multi-word phrases
        ]
        
        result = filtered_phrases[:top_n]
        print(f"Extracted key phrases: {result}")
        return result
    except Exception as e:
        print(f"Error in phrase extraction: {str(e)}")
        return []

def analyze_reviews(reviews: List[Dict[str, Any]]) -> InsightAnalysis:
    """
    Perform comprehensive NLP analysis on reviews.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        InsightAnalysis object with sentiment, keywords, and insights
    """
    if not reviews:
        print("No reviews to analyze")
        return InsightAnalysis(
            sentiment=SentimentAnalysis(
                overall_sentiment="NEUTRAL",
                sentiment_score=0.0,
                sentiment_distribution={"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0},
                confidence=0.0
            ),
            # keywords=KeywordAnalysis(
            #     common_keywords=[],
            #     negative_keywords=[],
            #     key_phrases=[]
            # ),
            # improvement_areas=[],
            # strengths=[],
            # weaknesses=[]
        )
    
    print(f"Analyzing {len(reviews)} reviews")
    
    # Combine all review texts
    all_text = " ".join(review.get('review_text', '') for review in reviews)
    # negative_text = " ".join(
    #     review.get('review_text', '')
    #     for review in reviews
    #     if review.get('rating', 0) <= 2
    # )
    
    print(f"Combined text length: {len(all_text)}")
    print(f"Sample of combined text: {all_text[:200]}...")
    
    # Sentiment Analysis
    sentiments = []
    scores = []
    confidences = []
    
    for review in reviews:
        sentiment, score, confidence = get_sentiment(review.get('review_text', ''))
        sentiments.append(sentiment)
        scores.append(score)
        confidences.append(confidence)
        print(f"--------------------------------")
        print(f"Review: {review.get('review_text')}")
        print(f"Rating: {review.get('rating')}")
        print('\n')
        print(f"Sentiment: {sentiment}")
        print(f"Score: {score}")
        print(f"Confidence: {confidence}")
        print(f"--------------------------------")
    
    # Calculate overall sentiment based on normalized scores
    # Transform scores: POSITIVE (close to 1) -> 1, NEGATIVE (close to 0) -> -1
    normalized_scores = []
    for sentiment, score in zip(sentiments, scores):
        if sentiment == "POSITIVE":
            normalized_scores.append(score)
        else:  # NEGATIVE
            normalized_scores.append(-score)
    
    avg_score = sum(normalized_scores) / len(normalized_scores)
    # Convert back to 0-1 scale for consistency
    normalized_avg = (avg_score + 1) / 2
    
    print(f"==========================================")
    print(f"sum(scores): {sum(scores)}")
    print(f"len(scores): {len(scores)}")
    print(f"avg_score: {avg_score}")
    print(f"==========================================")

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
    
    print(f"Overall sentiment: {overall_sentiment} (score: {normalized_avg})")
    
    # Calculate sentiment distribution
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)
    sentiment_distribution = {
        sentiment: (count / total) * 100
        for sentiment, count in sentiment_counts.items()
    }
    
    print(f"Sentiment distribution: {sentiment_distribution}")
    
    # Keyword Analysis
    # print("\nStarting keyword analysis...")
    # common_keywords = extract_keywords(all_text)
    
    # # Negative keywords analysis
    # print("\nStarting negative keyword analysis...")
    # negative_keywords = extract_keywords(negative_text)
    
    # # Key phrases analysis
    # print("\nStarting key phrase analysis...")
    # key_phrases = extract_key_phrases(all_text)
    
    # # Generate Insights
    # improvement_areas = []
    # strengths = []
    # weaknesses = []
    
    # # Analyze negative keywords for improvement areas
    # for keyword in negative_keywords:
    #     if keyword['count'] > 6:  # Only consider frequently mentioned issues
    #         improvement_areas.append(f"Address issues related to '{keyword['word']}'")
    
    # # Analyze sentiment for strengths and weaknesses
    # positive_phrases = [
    #     phrase for phrase in key_phrases
    #     if get_sentiment(phrase)[0] == "positive"
    # ]
    # negative_phrases = [
    #     phrase for phrase in key_phrases
    #     if get_sentiment(phrase)[0] == "negative"
    # ]
    
    # strengths.extend(positive_phrases[:3])
    # weaknesses.extend(negative_phrases[:3])
    
    # print(f"Found {len(improvement_areas)} improvement areas")
    # print(f"Found {len(strengths)} strengths")
    # print(f"Found {len(weaknesses)} weaknesses")
    
    return InsightAnalysis(
        sentiment=SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=round(normalized_avg, 2),
            sentiment_distribution=sentiment_distribution,
            confidence=round(sum(confidences) / len(confidences), 2)
        ),
        # keywords=KeywordAnalysis(
        #     common_keywords=common_keywords,
        #     negative_keywords=negative_keywords,
        #     key_phrases=key_phrases
        # ),
        # improvement_areas=improvement_areas,
        # strengths=strengths,
        # weaknesses=weaknesses
    ) 