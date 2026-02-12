from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
import re


def extract_keywords_tfidf(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords using TF-IDF
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of extracted keywords
    """
    try:
        # Simple preprocessing
        # Split into sentences for TF-IDF
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            # If too few sentences, split into words and return most unique ones
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            # Return unique words (simple approach)
            unique_words = []
            seen = set()
            for word in words:
                if word not in seen and len(unique_words) < max_keywords:
                    seen.add(word)
                    unique_words.append(word)
            return unique_words[:max_keywords]
        
        # Use TF-IDF to find important words
        vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words='english',
            ngram_range=(1, 2),  # unigrams and bigrams
            min_df=1
        )
        
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get average TF-IDF scores
        avg_scores = tfidf_matrix.mean(axis=0).A1
        
        # Get top keywords
        top_indices = avg_scores.argsort()[-max_keywords:][::-1]
        keywords = [feature_names[i] for i in top_indices if avg_scores[i] > 0]
        
        return keywords
    
    except Exception as e:
        # Fallback to simple word frequency if TF-IDF fails
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        from collections import Counter
        
        # Common English stop words
        stop_words = set([
            'this', 'that', 'these', 'those', 'with', 'from', 'have', 'has',
            'will', 'been', 'were', 'was', 'are', 'the', 'and', 'for', 'not',
            'but', 'or', 'as', 'at', 'by', 'an', 'be', 'to', 'of', 'in', 'it',
            'is', 'on', 'that', 'this', 'with', 'was', 'for', 'are', 'but',
            'not', 'you', 'all', 'can', 'her', 'had', 'how', 'our', 'out',
            'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now',
            'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let',
            'put', 'say', 'she', 'too', 'use'
        ])
        
        filtered_words = [w for w in words if w not in stop_words]
        counter = Counter(filtered_words)
        
        return [word for word, _ in counter.most_common(max_keywords)]
