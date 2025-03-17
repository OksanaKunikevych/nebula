from typing import List, Dict, Any, Tuple
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from collections import Counter
from pydantic import BaseModel
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/brown')
    nltk.data.find('corpora/movie_reviews')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('brown')
    nltk.download('movie_reviews')
    nltk.download('omw-1.4')  # Open Multilingual Wordnet
    print("NLTK data download complete.")

class SentimentAnalysis(BaseModel):
    overall_sentiment: str  # positive, negative, or neutral
    sentiment_score: float  # -1 to 1
    sentiment_distribution: Dict[str, float]  # percentage of each sentiment
    confidence: float  # confidence in the sentiment analysis

class KeywordAnalysis(BaseModel):
    common_keywords: List[Dict[str, Any]]  # list of {word: count} for most common words
    negative_keywords: List[Dict[str, Any]]  # list of {word: count} for negative reviews
    key_phrases: List[str]  # important phrases extracted from reviews

class InsightAnalysis(BaseModel):
    sentiment: SentimentAnalysis
    keywords: KeywordAnalysis
    improvement_areas: List[str]  # suggested areas for improvement
    strengths: List[str]  # identified strengths
    weaknesses: List[str]  # identified weaknesses

def get_sentiment(text: str) -> Tuple[str, float, float]:
    """
    Analyze sentiment of text using TextBlob.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (sentiment, score, confidence)
    """
    if not text:
        return "neutral", 0.0, 0.0
    
    try:
        analysis = TextBlob(text)
        score = analysis.sentiment.polarity
        print(f"Sentiment analysis for text: '{text[:50]}...' - Score: {score}")
        
        # Determine sentiment
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Calculate confidence based on polarity strength
        confidence = abs(score)
        
        return sentiment, score, confidence
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutral", 0.0, 0.0

def extract_keywords(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extract important keywords from text.
    
    Args:
        text: Text to analyze
        top_n: Number of top keywords to return
        
    Returns:
        List of dictionaries with word and count
    """
    if not text:
        return []
    
    try:
        # Tokenize and tag parts of speech
        tokens = word_tokenize(text.lower())
        tagged = pos_tag(tokens)
        
        # Get stopwords
        stop_words = set(stopwords.words('english'))
        
        # Filter for nouns, adjectives, and verbs
        keywords = [
            word for word, tag in tagged
            if (tag.startswith('NN') or tag.startswith('JJ') or tag.startswith('VB'))
            and word not in stop_words
            and len(word) > 2
        ]
        
        # Count frequencies
        word_freq = Counter(keywords)
        
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
    Extract important phrases from text.
    
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
            if len(phrase.split()) >= 2  # Only multi-word phrases
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
                overall_sentiment="neutral",
                sentiment_score=0.0,
                sentiment_distribution={"positive": 0, "negative": 0, "neutral": 0},
                confidence=0.0
            ),
            keywords=KeywordAnalysis(
                common_keywords=[],
                negative_keywords=[],
                key_phrases=[]
            ),
            improvement_areas=[],
            strengths=[],
            weaknesses=[]
        )
    
    print(f"Analyzing {len(reviews)} reviews")
    
    # Debug: Print first review content
    if reviews:
        first_review = reviews[0]
        print("First review content:")
        print(f"Title: {first_review.get('title', 'No title')}")
        print(f"Body: {first_review.get('body', 'No body')}")
        print(f"Rating: {first_review.get('rating', 'No rating')}")
    
    # Combine all review texts
    all_text = " ".join(review.get('body', '') for review in reviews)
    negative_text = " ".join(
        review.get('body', '')
        for review in reviews
        if review.get('rating', 0) <= 2
    )
    
    print(f"Combined text length: {len(all_text)}")
    print(f"Negative text length: {len(negative_text)}")
    print(f"Sample of combined text: {all_text[:200]}...")
    
    # Sentiment Analysis
    sentiments = []
    scores = []
    confidences = []
    
    for review in reviews:
        sentiment, score, confidence = get_sentiment(review.get('body', ''))
        sentiments.append(sentiment)
        scores.append(score)
        confidences.append(confidence)
    
    # Calculate overall sentiment
    avg_score = sum(scores) / len(scores)
    overall_sentiment = (
        "positive" if avg_score > 0.1
        else "negative" if avg_score < -0.1
        else "neutral"
    )
    
    print(f"Overall sentiment: {overall_sentiment} (score: {avg_score})")
    
    # Calculate sentiment distribution
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)
    sentiment_distribution = {
        sentiment: (count / total) * 100
        for sentiment, count in sentiment_counts.items()
    }
    
    print(f"Sentiment distribution: {sentiment_distribution}")
    
    # Keyword Analysis with debug info
    print("\nStarting keyword analysis...")
    print("Sample of text for keyword extraction:", all_text[:100])
    
    try:
        # Tokenize and tag parts of speech
        tokens = word_tokenize(all_text.lower())
        print(f"Number of tokens: {len(tokens)}")
        print("Sample tokens:", tokens[:10])
        
        tagged = pos_tag(tokens)
        print("Sample tagged tokens:", tagged[:10])
        
        # Get stopwords
        stop_words = set(stopwords.words('english'))
        print(f"Number of stopwords: {len(stop_words)}")
        
        # Filter for nouns, adjectives, and verbs
        keywords = [
            word for word, tag in tagged
            if (tag.startswith('NN') or tag.startswith('JJ') or tag.startswith('VB'))
            and word not in stop_words
            and len(word) > 2
        ]
        print(f"Number of filtered keywords: {len(keywords)}")
        print("Sample filtered keywords:", keywords[:10])
        
        # Count frequencies
        word_freq = Counter(keywords)
        print("Sample word frequencies:", dict(word_freq.most_common(5)))
        
        common_keywords = [
            {"word": word, "count": count}
            for word, count in word_freq.most_common(10)
        ]
        print("Final common keywords:", common_keywords)
        
    except Exception as e:
        print(f"Error in keyword extraction: {str(e)}")
        common_keywords = []
    
    # Negative keywords analysis
    print("\nStarting negative keyword analysis...")
    try:
        negative_tokens = word_tokenize(negative_text.lower())
        negative_tagged = pos_tag(negative_tokens)
        negative_keywords = [
            word for word, tag in negative_tagged
            if (tag.startswith('NN') or tag.startswith('JJ') or tag.startswith('VB'))
            and word not in stop_words
            and len(word) > 2
        ]
        negative_freq = Counter(negative_keywords)
        negative_keywords = [
            {"word": word, "count": count}
            for word, count in negative_freq.most_common(10)
        ]
        print("Negative keywords:", negative_keywords)
    except Exception as e:
        print(f"Error in negative keyword extraction: {str(e)}")
        negative_keywords = []
    
    # Key phrases analysis
    print("\nStarting key phrase analysis...")
    try:
        blob = TextBlob(all_text)
        phrases = blob.noun_phrases
        print(f"Number of noun phrases found: {len(phrases)}")
        print("Sample phrases:", phrases[:5])
        
        filtered_phrases = [
            phrase for phrase in phrases
            if len(phrase.split()) >= 2
        ]
        key_phrases = filtered_phrases[:5]
        print("Final key phrases:", key_phrases)
    except Exception as e:
        print(f"Error in phrase extraction: {str(e)}")
        key_phrases = []
    
    # Generate Insights
    improvement_areas = []
    strengths = []
    weaknesses = []
    
    # Analyze negative keywords for improvement areas
    for keyword in negative_keywords:
        if keyword['count'] > 2:  # Only consider frequently mentioned issues
            improvement_areas.append(f"Address issues related to '{keyword['word']}'")
    
    # Analyze sentiment for strengths and weaknesses
    positive_phrases = [
        phrase for phrase in key_phrases
        if get_sentiment(phrase)[0] == "positive"
    ]
    negative_phrases = [
        phrase for phrase in key_phrases
        if get_sentiment(phrase)[0] == "negative"
    ]
    
    strengths.extend(positive_phrases[:3])
    weaknesses.extend(negative_phrases[:3])
    
    print(f"Found {len(improvement_areas)} improvement areas")
    print(f"Found {len(strengths)} strengths")
    print(f"Found {len(weaknesses)} weaknesses")
    
    return InsightAnalysis(
        sentiment=SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=round(avg_score, 2),
            sentiment_distribution=sentiment_distribution,
            confidence=round(sum(confidences) / len(confidences), 2)
        ),
        keywords=KeywordAnalysis(
            common_keywords=common_keywords,
            negative_keywords=negative_keywords,
            key_phrases=key_phrases
        ),
        improvement_areas=improvement_areas,
        strengths=strengths,
        weaknesses=weaknesses
    ) 