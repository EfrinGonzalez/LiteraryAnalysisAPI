from collections import Counter
import re
from app.services.sentiment import analyze_sentiment
from app.services.report_writer import generate_pdf_report

def analyze_text_file(text: str):
    words = re.findall(r'\b[a-záéíóúñü]+\b', text.lower())
    stopwords = set("""
    de la que el y a en se no es por un con una los las del al como más pero sus le ha o lo
    """.split())
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    top_words = Counter(filtered).most_common(10)
    sentiment = analyze_sentiment(text)

    output_path = "app/reports/report.pdf"
    generate_pdf_report(text, top_words, sentiment, output_path)

    return {
        "word_count": len(filtered),
        "top_words": top_words,
        "sentiment": sentiment,
        "report_path": output_path
    }