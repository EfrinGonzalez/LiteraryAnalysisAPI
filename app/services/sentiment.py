from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize VADER analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# Try to import transformers for smart mode (optional)
try:
    from transformers import pipeline
    import torch
    
    # Check if CUDA is available, otherwise use CPU
    device = 0 if torch.cuda.is_available() else -1
    
    # Load a small, efficient sentiment model
    # Using distilbert for speed and efficiency
    try:
        smart_sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=device
        )
        SMART_MODE_AVAILABLE = True
        logger.info("Smart mode (transformer-based) sentiment analysis loaded successfully")
    except Exception as e:
        SMART_MODE_AVAILABLE = False
        logger.warning(f"Failed to load transformer model: {e}. Smart mode will fall back to fast mode.")
        smart_sentiment_pipeline = None
except ImportError:
    SMART_MODE_AVAILABLE = False
    smart_sentiment_pipeline = None
    logger.info("Transformers not installed. Smart mode will use fast mode fallback.")


def analyze_sentiment_fast(text: str) -> Dict[str, Any]:
    """
    Fast sentiment analysis using VADER (lexicon-based)
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment scores and label
    """
    scores = vader_analyzer.polarity_scores(text)
    
    # Determine label based on compound score
    compound = scores['compound']
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "polarity_label": label,
        "polarity_score": compound,
        "compound": compound,
        "positive": scores['pos'],
        "negative": scores['neg'],
        "neutral": scores['neu'],
        "confidence": None  # VADER doesn't provide confidence
    }


def analyze_sentiment_smart(text: str) -> Dict[str, Any]:
    """
    Smart sentiment analysis using transformer model
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment scores and label
    """
    if not SMART_MODE_AVAILABLE or smart_sentiment_pipeline is None:
        logger.warning("Smart mode not available, falling back to fast mode")
        return analyze_sentiment_fast(text)
    
    try:
        # Truncate text if too long (transformers have token limits)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        # Get prediction
        result = smart_sentiment_pipeline(text)[0]
        
        # Convert label to standardized format
        label = result['label'].lower()
        score = result['score']
        
        # Map labels (different models may use different labels)
        if label in ['positive', 'pos', '1']:
            polarity_label = "positive"
            polarity_score = score
        elif label in ['negative', 'neg', '0']:
            polarity_label = "negative"
            polarity_score = -score
        else:
            polarity_label = "neutral"
            polarity_score = 0.0
        
        return {
            "polarity_label": polarity_label,
            "polarity_score": polarity_score,
            "confidence": score,
            "compound": None,
            "positive": score if polarity_label == "positive" else 0,
            "negative": score if polarity_label == "negative" else 0,
            "neutral": score if polarity_label == "neutral" else 0
        }
    except Exception as e:
        logger.error(f"Error in smart sentiment analysis: {e}. Falling back to fast mode.")
        return analyze_sentiment_fast(text)


def analyze_sentiment(text: str, mode: str = "fast") -> Dict[str, Any]:
    """
    Analyze sentiment using specified mode
    
    Args:
        text: Text to analyze
        mode: Analysis mode - "fast" (VADER) or "smart" (transformer)
        
    Returns:
        Dictionary with sentiment analysis results
    """
    if mode == "smart":
        return analyze_sentiment_smart(text)
    else:
        return analyze_sentiment_fast(text)


def get_model_info(mode: str) -> str:
    """Get information about the model being used"""
    if mode == "smart" and SMART_MODE_AVAILABLE:
        return "distilbert-base-uncased-finetuned-sst-2-english"
    return "VADER (vaderSentiment)"
