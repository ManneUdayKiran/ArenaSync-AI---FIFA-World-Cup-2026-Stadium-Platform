from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_http_home_page():
    """Verify that home page GET request responds 200 and includes header timing metrics."""
    response = client.get("/")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers

def test_http_health_diagnostics():
    """Verify that health diagnostics endpoint matches operational fields."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "groq_sdk_enabled" in data
    assert "api_key_configured" in data

def test_api_assistant_chat_endpoint():
    """Verify assistant POST endpoint handles validation and multilingual logic."""
    # 1. Valid request
    payload = {
        "user_role": "fan",
        "message": "bag limit details",
        "history": [],
        "language": "es"
    }
    response = client.post("/api/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["detected_language"] == "es"
    
    # 2. Invalid role payload boundary check
    payload_invalid = {
        "user_role": "fan",
        "language": "en"
        # message missing
    }
    response_invalid = client.post("/api/assistant/chat", json=payload_invalid)
    assert response_invalid.status_code == 422

def test_api_gates_traffic_endpoint():
    """Verify gates traffic status returns correct array format."""
    response = client.get("/api/operations/gates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]["gate"] is not None

def test_api_incidents_lifecycle():
    """Verify complete logging, planning, and resolving workflows via API endpoints."""
    # 1. Log incident
    payload = {
        "title": "Water leakage in sector 331",
        "description": "Restroom pipe leak causing water puddle in section 331 exit stairs.",
        "zone": "Section 331 Exit Stairs",
        "severity": "Medium"
    }
    response = client.post("/api/operations/incidents", json=payload)
    assert response.status_code == 200
    inc = response.json()
    inc_id = inc["id"]
    assert inc["status"] == "Open"
    
    # 2. Generate AI resolution plan
    response_plan = client.post(f"/api/operations/incidents/{inc_id}/ai-plan")
    assert response_plan.status_code == 200
    plan_data = response_plan.json()
    assert plan_data["incident_id"] == inc_id
    assert "response_plan" in plan_data
    
    # 3. Resolve ticket
    response_resolve = client.post(f"/api/operations/incidents/{inc_id}/resolve")
    assert response_resolve.status_code == 200
    assert "Resolved successfully" in response_resolve.json()["message"]

def test_api_sustainability_endpoints():
    """Verify sustainability scan classification and score logging metrics."""
    # 1. Analyze waste scan
    response_scan = client.post("/api/sustainability/analyze", json={"item_id": "plastic_bottle"})
    assert response_scan.status_code == 200
    assert response_scan.json()["target_bin"] == "Recycle (Blue Bin)"
    
    # 2. Log points
    response_pts = client.post("/api/sustainability/add-points?username=EcoStriker&points=10&co2_saved_kg=2.0")
    assert response_pts.status_code == 200
    assert response_pts.json()["username"] == "EcoStriker"
    
    # 3. Check Leaderboard
    response_lb = client.get("/api/sustainability/leaderboard")
    assert response_lb.status_code == 200
    leaderboard = response_lb.json()["leaderboard"]
    assert any(entry["username"] == "EcoStriker" for entry in leaderboard)
