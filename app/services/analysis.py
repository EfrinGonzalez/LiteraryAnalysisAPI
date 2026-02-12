from collections import Counter
import re
import hashlib
from typing import Dict, Any
from app.services.sentiment import analyze_sentiment, get_model_info
from app.services.keywords import extract_keywords_tfidf


def analyze_text(text: str, mode: str = "fast") -> Dict[str, Any]:
    """
    Perform comprehensive text analysis
    
    Args:
        text: Text to analyze
        mode: Analysis mode - "fast" or "smart"
        
    Returns:
        Dictionary with analysis results including sentiment, keywords, and word stats
    """
    # Basic word analysis
    words = re.findall(r'\b[a-záéíóúñü]+\b', text.lower())
    
    # Common stop words (Spanish and English)
    stopwords = set("""
    de la que el y a en se no es por un con una los las del al como más pero sus le ha o lo
    the and to of in is it you that he was for on are with as they be at one have this from
    """.split())
    
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Get top words
    word_counts = Counter(filtered).most_common(10)
    
    # Sentiment analysis
    sentiment = analyze_sentiment(text, mode=mode)
    
    # Extract keywords
    keywords = extract_keywords_tfidf(text, max_keywords=10)
    
    # Build result
    result = {
        "word_count": len(filtered),
        "sentiment": sentiment,
        "keywords": keywords,
        "top_words": word_counts
    }
    
    return result


def compute_text_hash(text: str) -> str:
    """Compute SHA-256 hash of text for deduplication"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def analyze_text_file(text: str):
    """Legacy function for backward compatibility - deprecated"""
    from app.services.report_writer import generate_pdf_report
    
    words = re.findall(r'\b[a-záéíóúñü]+\b', text.lower())
    stopwords = set("""
    de la que el y a en se no es por un con una los las del al como más pero sus le ha o lo
    """.split())
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    top_words = Counter(filtered).most_common(10)
    
    # Use old sentiment format for compatibility
    sentiment_new = analyze_sentiment(text, mode="fast")
    sentiment = {
        "polarity": sentiment_new.get("polarity_score", 0),
        "subjectivity": 0.5  # Not available in VADER
    }

    output_path = "app/reports/report.pdf"
    try:
        generate_pdf_report(text, top_words, sentiment, output_path)
    except Exception:
        pass  # Ignore report generation errors

    return {
        "word_count": len(filtered),
        "top_words": top_words,
        "sentiment": sentiment,
        "report_path": output_path
    }
