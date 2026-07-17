import random
from app.services.simulator import StadiumSimulator

def test_simulator_gate_initialization():
    """Verify that all four MetLife gates are registered with occupancy properties."""
    sim = StadiumSimulator()
    gates = sim.get_gates()
    assert len(gates) == 4
    gate_names = [g["gate"] for g in gates]
    assert "Gate A (East)" in gate_names
    assert "Gate B (North)" in gate_names
    assert "Gate C (West)" in gate_names
    assert "Gate D (South)" in gate_names

def test_simulator_gate_noise_simulation():
    """Verify that get_gates mutates occupancies dynamically (noise check)."""
    sim = StadiumSimulator()
    # Fetch first state
    gates_state1 = {g["gate"]: g["current_occupancy"] for g in sim.get_gates()}
    
    # Fetch subsequent states multiple times to trigger noise checks
    for _ in range(5):
        sim.get_gates()
        
    gates_state2 = {g["gate"]: g["current_occupancy"] for g in sim.get_gates()}
    
    # Due to random noise variance (-150 to +150), states will differ
    assert gates_state1 != gates_state2

def test_simulator_incidents_management():
    """Verify state updates when logging and resolving operations tickets."""
    sim = StadiumSimulator()
    initial_open_count = len([inc for inc in sim.get_incidents() if inc["status"] == "Open"])
    
    # Create incident
    ticket = {
        "title": "Elevator B broken",
        "description": "Wheelchair guests are stranded near Gate B elevator entrance.",
        "zone": "Gate B",
        "severity": "High"
    }
    new_inc = sim.create_incident(ticket)
    assert new_inc["id"].startswith("INC-")
    assert new_inc["status"] == "Open"
    
    # Check count increased
    assert len([inc for inc in sim.get_incidents() if inc["status"] == "Open"]) == initial_open_count + 1
    
    # Resolve incident
    resolved = sim.resolve_incident(new_inc["id"])
    assert resolved is True
    assert new_inc["status"] == "Resolved"
    
    # Check count returned to normal
    assert len([inc for inc in sim.get_incidents() if inc["status"] == "Open"]) == initial_open_count

def test_simulator_sustainability_leaderboard():
    """Verify claims points updates standings rankings dynamically."""
    sim = StadiumSimulator()
    # Add high score for new player
    username = "GreenGod_2026"
    sim.add_sustainability_stats(username, 9999, 1500.0)
    
    leaderboard = sim.get_leaderboard()
    assert leaderboard[0]["username"] == username
    assert leaderboard[0]["points"] == 9999
    assert leaderboard[0]["co2_saved_kg"] == 1500.0
    
    # Add points to existing player
    sim.add_sustainability_stats(username, 1, 0.5)
    assert leaderboard[0]["points"] == 10000
