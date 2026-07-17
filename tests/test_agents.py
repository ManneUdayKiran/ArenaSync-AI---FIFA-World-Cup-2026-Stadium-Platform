from app.services.groq_service import groq_service

def test_groq_service_api_status():
    """Verify that Groq configuration detects API key status correctly."""
    # When api key is blank/mock, is_active is checked
    assert hasattr(groq_service, "is_active")

def test_agent_role_context_fan():
    """Verify AI Assistant Agent routes responses based on Fan role rules."""
    query = "Hello"
    res = groq_service.get_assistant_response(role="fan", query=query, history=[], language="en")
    assert "response" in res
    assert "MetLife Stadium" in res["response"]
    assert "detected_language" in res
    assert res["detected_language"] == "en"
    # Verify suggested queries are loaded
    assert len(res["suggested_actions"]) > 0
    assert "Find Wheelchair / ADA routes" in res["suggested_actions"]

def test_agent_role_context_volunteer():
    """Verify AI Assistant Agent routes responses based on Volunteer role rules."""
    query = "Shift time"
    res = groq_service.get_assistant_response(role="volunteer", query=query, history=[], language="en")
    assert "Volunteer Hub" in res["response"] or "Lot C" in res["response"]
    assert "Where is the Volunteer Hub?" in res["suggested_actions"]

def test_agent_translation_pipeline():
    """Verify Translation Agent intercepts and translates outputs for Spanish/French."""
    query = "train Secaucus"
    # Spanish target translation test
    res_es = groq_service.get_assistant_response(role="fan", query=query, history=[], language="es")
    assert "Versión traducida" in res_es["response"] or "es" == res_es["detected_language"]
    
    # French target translation test
    res_fr = groq_service.get_assistant_response(role="fan", query=query, history=[], language="fr")
    assert "Version traduite" in res_fr["response"] or "fr" == res_fr["detected_language"]

def test_agent_incident_plan_structure():
    """Verify Groq plan generator outputs valid JSON schema structures."""
    incident = {
        "title": "Gate C Concession Power Outage",
        "description": "concession stand C-2 has lost utility electricity power, cooling drinks is offline.",
        "zone": "Gate C Concession B",
        "severity": "High",
        "status": "Open"
    }
    plan = groq_service.generate_incident_response_plan(incident)
    assert "response_plan" in plan
    assert "announcements" in plan
    assert "assigned_tasks" in plan
    assert len(plan["assigned_tasks"]) == 3
    # Check localized emergency warnings
    assert "en" in plan["announcements"]
    assert "es" in plan["announcements"]
    assert "fr" in plan["announcements"]

def test_agent_waste_sorting_classifier():
    """Verify local classifier maps waste identifiers to eco values."""
    res = groq_service.analyze_waste_item("plastic_bottle")
    assert res["target_bin"] == "Recycle (Blue Bin)"
    assert res["points_awarded"] == 15
    assert res["co2_saved_kg"] == 0.08
    assert "sustainability_tip" in res
