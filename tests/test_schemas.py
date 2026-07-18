import pytest
from pydantic import ValidationError
from app.schemas.models import AssistantRequest, ChatMessage, IncidentCreate, WasteAnalysisRequest

def test_chat_message_schema():
    """Verify ChatMessage validators and restrictions."""
    # Happy path
    msg = ChatMessage(role="user", content="Hello assistant")
    assert msg.role == "user"
    assert msg.content == "Hello assistant"
    
    # Extra fields forbidden
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="Hi", extra_field="forbidden")

def test_assistant_request_schema():
    """Verify AssistantRequest validation, sanitization, and extra-field guards."""
    # Happy path
    req = AssistantRequest(user_role="fan", message="  Hello MetLife! \x00 ", language="en")
    assert req.user_role == "fan"
    # Control character \x00 stripped, whitespace trimmed
    assert req.message == "Hello MetLife!"
    assert req.language == "en"
    
    # Invalid role
    with pytest.raises(ValidationError):
        AssistantRequest(user_role="invalid_role", message="Hi")
        
    # Invalid language
    with pytest.raises(ValidationError):
        AssistantRequest(language="it", message="Hi")
        
    # Oversized string validation (should truncate or validate length limit of 500)
    oversized = "a" * 600
    req_large = AssistantRequest(message=oversized)
    assert len(req_large.message) == 500  # Sanitizer caps it to 500
    
    # Empty message (only control characters)
    with pytest.raises(ValidationError):
        AssistantRequest(message="\x00\x01\x02")

def test_waste_analysis_request_schema():
    """Verify WasteAnalysisRequest extra field constraints."""
    # Happy path
    req = WasteAnalysisRequest(item_id="plastic_bottle")
    assert req.item_id == "plastic_bottle"
    
    # Extra field forbidden
    with pytest.raises(ValidationError):
        WasteAnalysisRequest(item_id="plastic_bottle", scanner_type="auto")

def test_incident_create_schema():
    """Verify IncidentCreate strict stadium zone validators and severity enums."""
    # Happy path - Gate zone
    inc = IncidentCreate(title="Broken scanner", description="The scanner at Gate A is broken.", zone="Gate A", severity="High")
    assert inc.zone == "Gate A"
    assert inc.severity == "High"
    
    # Happy path - Section zone
    inc_sec = IncidentCreate(title="Liquid leak", description="Beer spill in section 120.", zone="Section 120", severity="Medium")
    assert inc_sec.zone == "Section 120"
    
    # Invalid zone name
    with pytest.raises(ValidationError):
        IncidentCreate(title="Broken scanner", description="Gate is down.", zone="Outside Stadium Area")
        
    # Invalid severity
    with pytest.raises(ValidationError):
        IncidentCreate(title="Broken scanner", description="Gate is down.", zone="Gate B", severity="Urgent")
        
    # Extra field forbidden
    with pytest.raises(ValidationError):
        IncidentCreate(title="Broken scanner", description="Gate is down.", zone="Gate B", reported_by="operator")
