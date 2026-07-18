from app.services.rag_store import search_rag, KNOWLEDGE_BASE

def test_wheelchair_accessibility_context():
    """Verify that wheelchair and ADA queries map to accessibility services grounding."""
    res = search_rag("Where can I find wheelchair accessible seating?")
    assert "accessibility" in res.lower()
    assert "ada" in res.lower()
    assert "elevator" in res.lower()

def test_visual_accessibility_context():
    """Verify visual assistance maps to guest services or sensory aids."""
    res = search_rag("Is there any assistance for blind or visually impaired fans?")
    assert "accessibility" in res.lower()
    assert "sensory" in res.lower()

def test_hearing_accessibility_context():
    """Verify hearing queries retrieve ALD assistive details."""
    res = search_rag("do you have listening devices or captions for deaf?")
    assert "listening devices" in res.lower()
    assert "accessibility" in res.lower()

def test_kickoff_urgency_context():
    """Verify kickoff queries route to gates and entrances hours."""
    res = search_rag("what time do gates open before kickoff?")
    assert "gates" in res.lower()
    assert "metlife stadium gates" in res.lower()

def test_high_crowd_transit_context():
    """Verify crowd transit queries match train or parking details."""
    res = search_rag("how to avoid post-game queues for secaucus trains?")
    assert "train" in res.lower()
    assert "nj transit" in res.lower()

def test_defensive_route_fallback():
    """Verify empty or random queries fallback gracefully to general stadium chunks."""
    res_empty = search_rag("")
    assert "fifa world cup 2026 overview" in res_empty.lower() or "gates" in res_empty.lower()
    
    res_random = search_rag("xyzkasldjfasdf")
    assert "overview" in res_random.lower()
