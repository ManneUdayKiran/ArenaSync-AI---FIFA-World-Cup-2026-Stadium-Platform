from app.services.rag_store import search_rag, KNOWLEDGE_BASE

def test_rag_search_overlap_success():
    """Verify that keyword overlap searches match relevant context documents."""
    # Searching for clear bag keywords should boost the bag policy document
    result = search_rag("What size clear bag can I bring?")
    assert "bag policy" in result.lower() or "clear bag" in result.lower()
    assert "12in x 6in x 12in" in result

def test_rag_search_transit_success():
    """Verify that transit searches match Meadowlands station information."""
    result = search_rag("how to take the train to MetLife?")
    assert "nj transit" in result.lower() or "meadowlands" in result.lower()
    assert "secaucus junction" in result.lower()

def test_rag_search_boost_weight():
    """Verify that search tags match boosts titles higher than descriptions."""
    # "sensory" is inside accessibility tags
    result = search_rag("sensory bags guest services")
    assert "sensory bags" in result.lower()
    assert "accessibility" in result.lower()

def test_rag_search_no_overlap_fallback():
    """Verify that a garbage search falls back to default general grounding context."""
    # A search with completely random words that don't match should return first 2 chunks
    result = search_rag("xyzqwertyasdfghjk")
    assert len(result) > 0
    # Checks that general World Cup context is present as a fallback
    assert "FIFA World Cup 2026" in result or "MetLife Stadium" in result
