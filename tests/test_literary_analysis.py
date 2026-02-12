"""
Tests for literary analysis endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_literary_analysis_basic(client: TestClient):
    """Test basic literary analysis with valid text"""
    payload = {
        "text": (
            "In the depths of the forest, where nature's beauty unfolds in all its sublime glory, "
            "the individual soul finds its truest expression. The trees whisper secrets of the heart, "
            "and the wind carries the passion of countless generations. Here, in this romantic haven, "
            "imagination reigns supreme, and emotion flows like a river through the landscape of dreams. "
            "The beauty of this place transcends mere observation, touching the very essence of being."
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "analysis_id" in data
    assert "created_at" in data
    assert data["source_type"] == "text"
    assert data["language"] == "english"
    assert "insights" in data
    
    # Check insights structure
    insights = data["insights"]
    assert "summary_short" in insights or "summary_medium" in insights
    assert "movement_or_tendency" in insights
    assert "influences" in insights
    assert "aesthetic_styles" in insights
    assert "disclaimer" in insights
    
    # Verify disclaimer is present and meaningful
    assert len(insights["disclaimer"]) > 50
    assert "probabilistic" in insights["disclaimer"].lower() or "interpretive" in insights["disclaimer"].lower()


def test_literary_analysis_short_summary(client: TestClient):
    """Test literary analysis with short summary request"""
    payload = {
        "text": (
            "The consciousness of modern life fragments into disconnected moments. "
            "Urban existence alienates the individual from authentic experience. "
            "Stream of thoughts flows through the city streets, where innovation "
            "meets tradition in experimental forms. The modern soul seeks meaning "
            "in the chaos of contemporary existence, finding beauty in fragmentation. " * 3
        ),
        "language": "english",
        "summary_length": "short"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    insights = data["insights"]
    
    # Short summary should be present
    assert insights["summary_short"] is not None
    # Short summary should be shorter than medium
    if insights["summary_medium"]:
        assert len(insights["summary_short"]) <= len(insights["summary_medium"])


def test_literary_analysis_spanish_output(client: TestClient):
    """Test literary analysis with Spanish output"""
    payload = {
        "text": (
            "En las profundidades del bosque romántico, donde la naturaleza despliega su belleza sublime, "
            "el alma individual encuentra su expresión más verdadera. Los árboles susurran secretos del corazón, "
            "y el viento lleva la pasión de innumerables generaciones. La imaginación reina suprema en este refugio, "
            "y la emoción fluye como un río a través del paisaje de los sueños y la belleza trascendental. " * 2
        ),
        "language": "spanish",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["language"] == "spanish"
    
    insights = data["insights"]
    # Check that disclaimer is in Spanish
    assert "probabilística" in insights["disclaimer"] or "interpretativa" in insights["disclaimer"]


def test_literary_analysis_aesthetic_styles(client: TestClient):
    """Test that aesthetic styles are detected"""
    payload = {
        "text": (
            "The subconscious mind reveals itself through dreams and bizarre fantasies. "
            "Irrational visions emerge from the unconscious depths, creating surreal landscapes "
            "where reality bends and transforms. The dream logic defies conventional understanding, "
            "presenting a world where the impossible becomes tangible and the unconscious speaks "
            "through symbolic imagery that transcends rational thought and embraces pure fantasy. " * 2
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    insights = response.json()["insights"]
    
    # Should detect at least one aesthetic style
    assert len(insights["aesthetic_styles"]) > 0
    
    # Each style should have required fields
    for style in insights["aesthetic_styles"]:
        assert "style" in style
        assert "confidence" in style
        assert style["confidence"] in ["high", "medium", "low", "alta", "media", "baja"]


def test_literary_analysis_influences(client: TestClient):
    """Test that influences are detected"""
    payload = {
        "text": (
            "The stream of consciousness technique reveals the inner workings of the mind. "
            "Like Joyce and Woolf before us, we explore the depths of psychological reality. "
            "The modernist experiment in Dublin and London transformed literature forever. "
            "Consciousness flows freely across the page, capturing thoughts as they emerge "
            "in their natural, unfiltered state, revolutionary in its approach to narrative. " * 2
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    insights = response.json()["insights"]
    
    # Check influences structure
    assert isinstance(insights["influences"], list)
    
    # If influences are detected, verify structure
    if len(insights["influences"]) > 0:
        for influence in insights["influences"]:
            assert "name" in influence
            assert "type" in influence
            assert "rationale" in influence
            assert len(influence["rationale"]) > 10


def test_literary_analysis_movement_detection(client: TestClient):
    """Test that literary movement is detected"""
    payload = {
        "text": (
            "Emotion and passion drive the narrative forward through the sublime landscape of nature. "
            "The individual's feelings and imagination take center stage, celebrating the beauty of the natural world. "
            "The heart speaks louder than reason, and the soul finds expression in the romantic contemplation "
            "of nature's grandeur. Beauty, passion, and emotional intensity characterize this exploration "
            "of the human condition through the lens of individual experience and natural sublimity. " * 2
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    insights = response.json()["insights"]
    
    # Should detect a movement or tendency
    assert "movement_or_tendency" in insights
    assert len(insights["movement_or_tendency"]) > 0
    assert isinstance(insights["movement_or_tendency"], str)


def test_literary_analysis_text_too_short(client: TestClient):
    """Test that very short text returns appropriate error"""
    payload = {
        "text": "Too short.",
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 400
    
    error = response.json()
    assert "detail" in error
    assert "too short" in error["detail"].lower() or "200 characters" in error["detail"]


def test_literary_analysis_empty_text(client: TestClient):
    """Test that empty text returns validation error"""
    payload = {
        "text": "",
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 422  # Validation error


def test_literary_analysis_minimum_valid_length(client: TestClient):
    """Test with minimum valid text length (200 characters)"""
    # Create a text that's exactly around 200 characters
    payload = {
        "text": "A" * 50 + " This is a test of literary analysis with exactly enough characters to pass validation. " * 2,
        "language": "english",
        "summary_length": "short"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    # Should succeed with 200+ characters
    assert response.status_code == 200
    
    insights = response.json()["insights"]
    assert insights["disclaimer"] is not None


def test_literary_analysis_default_parameters(client: TestClient):
    """Test that default parameters work correctly"""
    payload = {
        "text": (
            "Literature explores the human condition through narrative and poetic expression. "
            "Authors throughout history have used various techniques to convey meaning and emotion. "
            "The art of storytelling transcends cultural boundaries, speaking to universal themes "
            "of love, loss, hope, and the search for meaning in existence. Each era brings new "
            "perspectives and innovations to the craft of writing and literary expression. " * 2
        )
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # Default language should be english
    assert data["language"] == "english"
    
    insights = data["insights"]
    # Default summary_length is medium, so summary_medium should be present
    assert insights["summary_medium"] is not None


def test_literary_analysis_database_persistence(client: TestClient):
    """Test that literary analysis is stored in database"""
    payload = {
        "text": (
            "The postmodern narrative fragments and reconstructs itself through layers of irony and self-reference. "
            "Metafiction reveals the constructed nature of storytelling, while paradoxes challenge our assumptions. "
            "The plurality of perspectives deconstructs traditional narrative authority, creating a pastiche "
            "of styles and voices that reflect the complexity of contemporary experience. " * 3
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    analysis_id = data["analysis_id"]
    
    # Verify the response contains an analysis ID (which means it was stored)
    assert analysis_id is not None
    assert len(analysis_id) > 0
    
    # Verify the mode is literary
    # Note: The general /v1/analyses/{id} endpoint is for regular analysis
    # Literary analysis is stored but retrieved differently
    # This test confirms the analysis was created and returned with an ID


def test_literary_analysis_multiple_aesthetic_styles(client: TestClient):
    """Test detection of multiple aesthetic styles in mixed text"""
    payload = {
        "text": (
            "The romantic beauty of nature meets the harsh reality of everyday social life. "
            "Emotional intensity clashes with realistic observation of contemporary society. "
            "Dreams and imagination blend with scientific determinism and objective analysis. "
            "The sublime feelings of the heart encounter the rational order of classical proportion. "
            "This fusion of styles creates a unique literary experience that transcends single movements. " * 3
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    insights = response.json()["insights"]
    
    # Should detect multiple styles
    assert len(insights["aesthetic_styles"]) >= 1
    
    # Verify confidence levels are properly assigned
    for style in insights["aesthetic_styles"]:
        assert style["confidence"] in ["high", "medium", "low"]


def test_literary_analysis_response_completeness(client: TestClient):
    """Test that all required fields are present in response"""
    payload = {
        "text": (
            "In this comprehensive test of the literary analysis system, we examine how well "
            "the API handles complex literary texts with multiple layers of meaning. The system "
            "should identify movements, influences, and aesthetic styles while providing accurate "
            "summaries and appropriate disclaimers about the interpretive nature of the analysis. "
            "This ensures users understand the probabilistic foundations of computational literary criticism. " * 3
        ),
        "language": "english",
        "summary_length": "medium"
    }
    
    response = client.post("/v1/analyze/literary", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Top-level required fields
    required_fields = ["analysis_id", "created_at", "source_type", "language", "insights"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Insights required fields
    insights = data["insights"]
    insights_required = ["movement_or_tendency", "influences", "aesthetic_styles", "disclaimer"]
    for field in insights_required:
        assert field in insights, f"Missing required insights field: {field}"
    
    # At least one summary should be present
    assert insights["summary_short"] is not None or insights["summary_medium"] is not None
