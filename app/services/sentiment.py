from textblob import TextBlob

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    return {
        "polarity": round(blob.sentiment.polarity, 3),
        "subjectivity": round(blob.sentiment.subjectivity, 3)
    }