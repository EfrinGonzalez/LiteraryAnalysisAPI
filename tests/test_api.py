import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["database"] == "connected"


def test_analyze_text_fast_mode(client: TestClient):
    """Test text analysis with fast mode"""
    payload = {
        "text": "This is a wonderful and amazing product! I love it so much.",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/text", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "analysis_id" in data
    assert "created_at" in data
    assert data["source_type"] == "text"
    assert data["mode"] == "fast"
    
    # Check result structure
    result = data["result"]
    assert "word_count" in result
    assert "sentiment" in result
    assert "keywords" in result
    
    # Check sentiment structure
    sentiment = result["sentiment"]
    assert "polarity_label" in sentiment
    assert "polarity_score" in sentiment
    assert sentiment["polarity_label"] in ["positive", "negative", "neutral"]
    
    # For this positive text, expect positive sentiment
    assert sentiment["polarity_label"] == "positive"
    assert sentiment["polarity_score"] > 0


def test_analyze_text_validation(client: TestClient):
    """Test text analysis validation"""
    # Empty text should fail
    response = client.post("/v1/analyze/text", json={"text": "", "mode": "fast"})
    assert response.status_code == 422  # Validation error


def test_retrieve_analysis_by_id(client: TestClient):
    """Test retrieving an analysis by ID"""
    # First create an analysis
    payload = {
        "text": "This is a test text for retrieval.",
        "mode": "fast"
    }
    
    create_response = client.post("/v1/analyze/text", json=payload)
    assert create_response.status_code == 200
    
    analysis_id = create_response.json()["analysis_id"]
    
    # Now retrieve it
    get_response = client.get(f"/v1/analyses/{analysis_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["analysis_id"] == analysis_id
    assert data["source_type"] == "text"
    assert "result" in data


def test_retrieve_nonexistent_analysis(client: TestClient):
    """Test retrieving a non-existent analysis"""
    response = client.get("/v1/analyses/nonexistent-id-12345")
    assert response.status_code == 404


def test_list_analyses(client: TestClient):
    """Test listing analyses"""
    # Create a few analyses
    for i in range(3):
        payload = {
            "text": f"Test text number {i}",
            "mode": "fast"
        }
        client.post("/v1/analyze/text", json=payload)
    
    # List all analyses
    response = client.get("/v1/analyses")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "analyses" in data
    assert data["total"] == 3
    assert len(data["analyses"]) == 3


def test_list_analyses_with_filters(client: TestClient):
    """Test listing analyses with filters"""
    # Create some analyses
    client.post("/v1/analyze/text", json={"text": "Test text", "mode": "fast"})
    
    # List with filter
    response = client.get("/v1/analyses?source_type=text&limit=5&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_list_analyses_pagination(client: TestClient):
    """Test pagination in list analyses"""
    # Create multiple analyses
    for i in range(5):
        client.post("/v1/analyze/text", json={"text": f"Text {i}", "mode": "fast"})
    
    # Get first page
    response1 = client.get("/v1/analyses?limit=2&offset=0")
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["analyses"]) == 2
    assert data1["total"] == 5
    
    # Get second page
    response2 = client.get("/v1/analyses?limit=2&offset=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["analyses"]) == 2


def test_negative_sentiment(client: TestClient):
    """Test negative sentiment detection"""
    payload = {
        "text": "This is terrible, awful, and horrible. I hate it.",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/text", json=payload)
    assert response.status_code == 200
    
    sentiment = response.json()["result"]["sentiment"]
    assert sentiment["polarity_label"] == "negative"
    assert sentiment["polarity_score"] < 0


def test_neutral_sentiment(client: TestClient):
    """Test neutral sentiment detection"""
    payload = {
        "text": "The door is blue. The table is wooden.",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/text", json=payload)
    assert response.status_code == 200
    
    sentiment = response.json()["result"]["sentiment"]
    assert sentiment["polarity_label"] == "neutral"


def test_keyword_extraction(client: TestClient):
    """Test that keywords are extracted"""
    payload = {
        "text": "Python programming is great for machine learning and data science. "
                "Many developers love Python for its simplicity and powerful libraries.",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/text", json=payload)
    assert response.status_code == 200
    
    keywords = response.json()["result"]["keywords"]
    assert isinstance(keywords, list)
    assert len(keywords) > 0
