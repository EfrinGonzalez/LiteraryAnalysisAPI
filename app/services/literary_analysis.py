"""
Literary analysis service for advanced text insights.

This module provides enhanced literary analysis including summaries, movements,
influences, and aesthetic styles. The analysis is probabilistic and interpretive.
"""

import re
import logging
from typing import Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)

# Literary movement keywords (expanded for better detection)
MOVEMENT_KEYWORDS = {
    "romanticism": ["emotion", "nature", "imagination", "individual", "passion", "sublime", "feeling", "heart", "soul", "beauty"],
    "realism": ["reality", "ordinary", "everyday", "society", "social", "realistic", "life", "contemporary", "observation"],
    "modernism": ["consciousness", "fragmentation", "alienation", "stream", "experimental", "innovation", "urban", "modern"],
    "postmodernism": ["irony", "metafiction", "paradox", "self-referential", "pastiche", "deconstruction", "plurality"],
    "symbolism": ["symbol", "metaphor", "abstract", "spiritual", "mystical", "dream", "vision", "transcendent"],
    "naturalism": ["determinism", "survival", "environment", "instinct", "heredity", "scientific", "objective"],
    "surrealism": ["subconscious", "dream", "irrational", "unconscious", "bizarre", "fantasy", "surreal"],
    "classicism": ["order", "harmony", "reason", "balance", "proportion", "rational", "classical", "tradition"],
    "expressionism": ["distortion", "emotional", "subjective", "exaggeration", "intensity", "inner", "psychological"],
    "existentialism": ["existence", "freedom", "absurd", "choice", "responsibility", "meaning", "authentic", "being"]
}

# Influential authors and their associated styles
INFLUENTIAL_AUTHORS = {
    "shakespeare": ["drama", "theatre", "tragedy", "comedy", "sonnet", "elizabethan"],
    "cervantes": ["quixote", "knight", "chivalry", "satire", "picaresque"],
    "homer": ["epic", "odyssey", "iliad", "hero", "greek", "classical"],
    "dante": ["inferno", "divine", "hell", "paradise", "medieval"],
    "dostoyevsky": ["underground", "psychological", "crime", "punishment", "russian"],
    "tolstoy": ["war", "peace", "anna", "karenina", "russian", "epic"],
    "joyce": ["ulysses", "stream", "consciousness", "modernist", "dublin"],
    "kafka": ["metamorphosis", "trial", "absurd", "bureaucracy", "alienation"],
    "woolf": ["waves", "lighthouse", "orlando", "stream", "consciousness"],
    "proust": ["remembrance", "time", "past", "memory", "introspection"],
    "faulkner": ["yoknapatawpha", "south", "american", "stream", "consciousness"],
    "borges": ["labyrinth", "mirror", "infinity", "metaphysical", "argentine"],
    "garcia marquez": ["solitude", "magical", "realism", "macondo", "colombian"],
    "hemingway": ["old man", "sea", "arms", "sun", "sparse", "direct"],
    "poe": ["raven", "gothic", "horror", "detective", "macabre"],
    "dickens": ["expectation", "twist", "tale", "cities", "victorian"],
    "austen": ["pride", "prejudice", "sense", "sensibility", "manners"],
    "bronte": ["jane eyre", "wuthering", "heights", "gothic", "romantic"]
}

# Philosophical and cultural movements
PHILOSOPHICAL_INFLUENCES = {
    "enlightenment": ["reason", "rational", "progress", "science", "empirical"],
    "romanticism": ["emotion", "nature", "individual", "imagination", "sublime"],
    "marxism": ["class", "proletariat", "capitalism", "revolution", "economic"],
    "freudian": ["unconscious", "psychoanalysis", "id", "ego", "dream"],
    "nietzschean": ["superman", "will", "power", "nihilism", "morality"],
    "existentialism": ["existence", "freedom", "absurd", "authentic", "being"],
    "structuralism": ["structure", "system", "sign", "language", "binary"],
    "poststructuralism": ["deconstruction", "difference", "trace", "supplement"],
    "feminism": ["gender", "women", "patriarchy", "equality", "feminist"],
    "postcolonialism": ["colonial", "empire", "identity", "hybridity", "subaltern"]
}


def extract_text_features(text: str) -> Dict[str, Any]:
    """Extract features from text for analysis"""
    # Clean and tokenize
    text_lower = text.lower()
    words = re.findall(r'\b[a-záéíóúñü]+\b', text_lower)
    
    # Remove common stop words
    stopwords = set("""
    de la que el y a en se no es por un con una los las del al como más pero sus le ha o lo
    the and to of in is it you that he was for on are with as they be at one have this from
    i we or an my their which what can would will been been has had been do did does but so
    if all some any each much many other such about up out into through than then now
    """.split())
    
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
    
    return {
        "text": text,
        "text_lower": text_lower,
        "words": words,
        "filtered_words": filtered_words,
        "word_count": len(filtered_words),
        "char_count": len(text)
    }


def detect_literary_movement(features: Dict[str, Any]) -> Dict[str, float]:
    """Detect literary movements based on keyword analysis"""
    text_lower = features["text_lower"]
    filtered_words = features["filtered_words"]
    word_set = set(filtered_words)
    
    movement_scores = {}
    
    for movement, keywords in MOVEMENT_KEYWORDS.items():
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        # Normalize by number of keywords and text length
        score = matches / max(len(keywords), 1)
        movement_scores[movement] = score
    
    return movement_scores


def detect_influences(features: Dict[str, Any]) -> List[Dict[str, str]]:
    """Detect potential influences from authors, philosophies, and schools"""
    text_lower = features["text_lower"]
    influences = []
    
    # Check for author influences
    for author, keywords in INFLUENTIAL_AUTHORS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches >= 1:
            influences.append({
                "name": author.title(),
                "type": "author",
                "confidence": "medium" if matches > 1 else "low"
            })
    
    # Check for philosophical influences
    for philosophy, keywords in PHILOSOPHICAL_INFLUENCES.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches >= 2:
            influences.append({
                "name": philosophy.title(),
                "type": "philosophy",
                "confidence": "medium" if matches > 2 else "low"
            })
    
    # Limit to top 5 influences
    return influences[:5]


def generate_summary(text: str, length: str = "medium") -> str:
    """Generate a summary of the text"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return "Text is too short to generate a meaningful summary."
    
    if length == "short":
        # Take first 1-2 sentences
        num_sentences = min(2, len(sentences))
        summary = ". ".join(sentences[:num_sentences])
        # Limit to ~100 words
        words = summary.split()
        if len(words) > 100:
            summary = " ".join(words[:100]) + "..."
        return summary + "."
    else:  # medium
        # Take first 3-5 sentences
        num_sentences = min(5, max(3, len(sentences) // 3))
        summary = ". ".join(sentences[:num_sentences])
        # Limit to ~200 words
        words = summary.split()
        if len(words) > 200:
            summary = " ".join(words[:200]) + "..."
        return summary + "."


def analyze_literary_text(
    text: str, 
    language: str = "english",
    summary_length: str = "medium"
) -> Dict[str, Any]:
    """
    Perform comprehensive literary analysis on text.
    
    Args:
        text: Text to analyze
        language: Output language (english or spanish)
        summary_length: Length of summary (short or medium)
        
    Returns:
        Dictionary with literary insights
    """
    # Validate input length
    if len(text) < 200:
        raise ValueError(
            "Text is too short for literary analysis. "
            "Please provide at least 200 characters for meaningful insights."
        )
    
    # Extract features
    features = extract_text_features(text)
    
    # Generate summaries
    summary_short = generate_summary(text, "short")
    summary_medium = generate_summary(text, "medium")
    
    # Detect literary movement
    movement_scores = detect_literary_movement(features)
    top_movement = max(movement_scores.items(), key=lambda x: x[1])
    
    # Select primary movement (only if score is meaningful)
    if top_movement[1] > 0.1:
        primary_movement = top_movement[0].title()
    else:
        primary_movement = "Contemporary/Mixed"
    
    # Detect influences
    raw_influences = detect_influences(features)
    
    # Format influences with rationale
    influences = []
    for inf in raw_influences:
        rationale = f"Detected through thematic and stylistic elements characteristic of {inf['name']}"
        influences.append({
            "name": inf["name"],
            "type": inf["type"],
            "rationale": rationale
        })
    
    # Determine aesthetic styles
    aesthetic_styles = []
    # Get top 3 movements with meaningful scores
    sorted_movements = sorted(movement_scores.items(), key=lambda x: x[1], reverse=True)
    for movement, score in sorted_movements[:3]:
        if score > 0.05:
            confidence = "high" if score > 0.3 else "medium" if score > 0.15 else "low"
            aesthetic_styles.append({
                "style": movement.title(),
                "confidence": confidence
            })
    
    # If no styles detected, add a default
    if not aesthetic_styles:
        aesthetic_styles.append({
            "style": "Contemporary",
            "confidence": "low"
        })
    
    # Prepare disclaimer
    disclaimers = {
        "english": (
            "This analysis is probabilistic and interpretive in nature. "
            "The identified movements, influences, and styles are suggestions based on "
            "computational text analysis and should not be considered definitive literary criticism. "
            "Human expert analysis may yield different interpretations."
        ),
        "spanish": (
            "Este análisis es de naturaleza probabilística e interpretativa. "
            "Los movimientos, influencias y estilos identificados son sugerencias basadas en "
            "análisis computacional de texto y no deben considerarse crítica literaria definitiva. "
            "El análisis de expertos humanos puede producir interpretaciones diferentes."
        )
    }
    
    disclaimer = disclaimers.get(language, disclaimers["english"])
    
    # Translate fields if Spanish requested
    if language == "spanish":
        primary_movement = translate_movement_to_spanish(primary_movement)
        aesthetic_styles = translate_styles_to_spanish(aesthetic_styles)
        influences = translate_influences_to_spanish(influences)
    
    return {
        "summary_short": summary_short if summary_length in ["short", "medium"] else None,
        "summary_medium": summary_medium if summary_length == "medium" else None,
        "movement_or_tendency": primary_movement,
        "influences": influences,
        "aesthetic_styles": aesthetic_styles,
        "disclaimer": disclaimer
    }


def translate_movement_to_spanish(movement: str) -> str:
    """Translate movement names to Spanish"""
    translations = {
        "Romanticism": "Romanticismo",
        "Realism": "Realismo",
        "Modernism": "Modernismo",
        "Postmodernism": "Posmodernismo",
        "Symbolism": "Simbolismo",
        "Naturalism": "Naturalismo",
        "Surrealism": "Surrealismo",
        "Classicism": "Clasicismo",
        "Expressionism": "Expresionismo",
        "Existentialism": "Existencialismo",
        "Contemporary/Mixed": "Contemporáneo/Mixto",
        "Contemporary": "Contemporáneo"
    }
    return translations.get(movement, movement)


def translate_styles_to_spanish(styles: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Translate aesthetic styles to Spanish"""
    confidence_map = {
        "high": "alta",
        "medium": "media",
        "low": "baja"
    }
    
    translated = []
    for style in styles:
        translated.append({
            "style": translate_movement_to_spanish(style["style"]),
            "confidence": confidence_map.get(style["confidence"], style["confidence"])
        })
    return translated


def translate_influences_to_spanish(influences: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Translate influence types and rationale to Spanish"""
    type_map = {
        "author": "autor",
        "philosophy": "filosofía",
        "school": "escuela",
        "historical": "histórico",
        "cultural": "cultural"
    }
    
    translated = []
    for inf in influences:
        rationale = inf["rationale"].replace(
            "Detected through thematic and stylistic elements characteristic of",
            "Detectado a través de elementos temáticos y estilísticos característicos de"
        )
        translated.append({
            "name": inf["name"],
            "type": type_map.get(inf["type"], inf["type"]),
            "rationale": rationale
        })
    return translated
