import pytest
from unittest.mock import patch
from app.services.scraper import is_safe_url


def test_ssrf_localhost_blocked():
    """Test that localhost is blocked"""
    assert is_safe_url("http://localhost/api") == False
    assert is_safe_url("http://127.0.0.1/api") == False
    assert is_safe_url("http://127.0.0.2/api") == False


def test_ssrf_private_ips_blocked():
    """Test that private IP ranges are blocked"""
    # Class A private
    assert is_safe_url("http://10.0.0.1/api") == False
    assert is_safe_url("http://10.255.255.255/api") == False
    
    # Class B private
    assert is_safe_url("http://172.16.0.1/api") == False
    assert is_safe_url("http://172.31.255.255/api") == False
    
    # Class C private
    assert is_safe_url("http://192.168.0.1/api") == False
    assert is_safe_url("http://192.168.255.255/api") == False
    
    # Link-local
    assert is_safe_url("http://169.254.0.1/api") == False


@patch('socket.gethostbyname')
def test_ssrf_public_urls_allowed(mock_gethostbyname):
    """Test that public URLs are allowed"""
    # Mock DNS resolution to return a public IP
    mock_gethostbyname.return_value = "93.184.216.34"  # example.com IP
    
    assert is_safe_url("http://example.com/api") == True
    assert is_safe_url("https://example.com/api") == True


def test_ssrf_invalid_schemes_blocked():
    """Test that non-HTTP(S) schemes are blocked"""
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("ftp://example.com") == False
    assert is_safe_url("javascript:alert(1)") == False


def test_ssrf_ipv6_localhost_blocked():
    """Test that IPv6 localhost is blocked"""
    assert is_safe_url("http://[::1]/api") == False


def test_analyze_url_ssrf_protection(client):
    """Test that URL analysis endpoint blocks SSRF attempts"""
    # Try to analyze localhost
    payload = {
        "url": "http://localhost:8000/health",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/url", json=payload)
    # Should get 400 error due to SSRF protection
    assert response.status_code == 400
    assert "blocked" in response.json()["detail"].lower() or "security" in response.json()["detail"].lower()


def test_analyze_url_private_ip_blocked(client):
    """Test that private IP addresses are blocked"""
    payload = {
        "url": "http://192.168.1.1/admin",
        "mode": "fast"
    }
    
    response = client.post("/v1/analyze/url", json=payload)
    assert response.status_code == 400
