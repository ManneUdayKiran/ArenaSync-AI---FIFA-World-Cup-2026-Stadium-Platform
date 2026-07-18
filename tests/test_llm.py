import pytest
from app.services.groq_service import GroqService

def test_groq_service_mock_fallback():
    """Verify that GroqService handles missing keys gracefully by falling back to simulation."""
    # Create instance with empty key
    from app.config import settings
    original_key = settings.GROQ_API_KEY
    settings.GROQ_API_KEY = ""
    
    svc = GroqService()
    assert svc.is_active is False
    
    # Verify mock response is generated
    res = svc.get_assistant_response(role="fan", query="Where is Gate A?", history=[], language="en")
    assert "response" in res
    assert "detected_language" in res
    assert len(res["suggested_actions"]) > 0
    
    # Restore key
    settings.GROQ_API_KEY = original_key

def test_groq_service_call_api_error_fallback():
    """Verify that calling the API on failure falls back to mock responses gracefully."""
    svc = GroqService()
    
    # Force API active but corrupt url to trigger failure/fallback
    svc.is_active = True
    svc.api_url = "https://invalid.groq.com/v1/chat"
    
    res = svc.get_assistant_response(role="volunteer", query="Lot C check in hours", history=[], language="en")
    assert "response" in res
    assert "detected_language" in res
    # Fallback should kick in and serve mock volunteer answers
    assert "Lot C Volunteer Hub" in res["response"]
