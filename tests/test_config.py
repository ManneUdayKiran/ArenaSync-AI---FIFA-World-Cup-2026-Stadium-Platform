import os
from app.config import settings

def test_project_configuration():
    """Verify that configuration settings load basic metadata correctly."""
    assert settings.PROJECT_NAME == "ArenaSync AI"
    assert settings.VERSION == "1.0.0"
    assert settings.RATE_LIMIT_PER_MINUTE == 60

def test_stadium_name_default():
    """Verify that MetLife is the default stadium configuration."""
    assert "MetLife Stadium" in settings.STADIUM_NAME

def test_groq_model_name():
    """Verify default Groq model configuration aligns with requirements."""
    assert settings.GROQ_MODEL == "openai/gpt-oss-120b"
