import random
import time
from datetime import datetime
from typing import List, Dict

class StadiumSimulator:
    def __init__(self):
        # Setup gates default state
        self.gates = {
            "Gate A (East)": {
                "gate": "Gate A (East)",
                "current_occupancy": 3200,
                "max_capacity": 10000,
                "wait_time_minutes": 6,
                "congestion_level": "Low",
                "recommended_action": "Proceed directly. Short queues, minimal delay."
            },
            "Gate B (North)": {
                "gate": "Gate B (North)",
                "current_occupancy": 8800,
                "max_capacity": 10000,
                "wait_time_minutes": 29,
                "congestion_level": "High",
                "recommended_action": "Avoid. Heavy bottlenecks. Reroute to Gate A (East) or Gate D (South)."
            },
            "Gate C (West)": {
                "gate": "Gate C (West)",
                "current_occupancy": 6400,
                "max_capacity": 10000,
                "wait_time_minutes": 16,
                "congestion_level": "Medium",
                "recommended_action": "Moderate queues. Expect 15-20 min wait. VIP entry at Gate C remains open."
            },
            "Gate D (South)": {
                "gate": "Gate D (South)",
                "current_occupancy": 2100,
                "max_capacity": 10000,
                "wait_time_minutes": 4,
                "congestion_level": "Low",
                "recommended_action": "Recommended. Nearest entry for Meadowlands Rail Station arrivals."
            }
        }
        
        # Setup pre-defined open incidents
        self.incidents = [
            {
                "id": "INC-0922",
                "title": "Gate B Ticket Scanner Malfunction",
                "description": "Two electronic scanning turnstiles at Gate B are offline. Crowds are stacking up at the northern entrance.",
                "zone": "Gate B (North) Entrance",
                "severity": "High",
                "status": "Open",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "INC-3810",
                "title": "Lost Child at Family Zone",
                "description": "An 8-year-old child wearing a green Mexico jersey separated from parents near the Section 124 Guest Services Desk.",
                "zone": "Section 124 Guest Services",
                "severity": "Medium",
                "status": "Open",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "INC-7419",
                "title": "Recycle Bin Obstruction",
                "description": "Compost bin B-3 is full and blocking the wheelchair-accessible ramp near Section 201.",
                "zone": "Section 201 ADA Ramp",
                "severity": "Low",
                "status": "Open",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        self.sustainability_points = 12450  # Global eco-points pool for demo
        self.co2_saved = 4120.5  # Global carbon footprint savings tracker
        self.leaderboard = [
            {"username": "EcoFan_US", "points": 850, "co2_saved_kg": 255.0},
            {"username": "TriColor_26", "points": 720, "co2_saved_kg": 216.0},
            {"username": "MapleLeafAero", "points": 680, "co2_saved_kg": 204.0},
            {"username": "StadiumSaviour", "points": 610, "co2_saved_kg": 183.0},
            {"username": "GreenStriker", "points": 590, "co2_saved_kg": 177.0}
        ]

    def get_gates(self) -> List[Dict]:
        """Dynamically simulate minor gate queue variations & return all gate states."""
        for gate_name, data in self.gates.items():
            # Add small random noise to make the UI look alive
            noise = random.randint(-150, 150)
            new_occ = max(1000, min(data["max_capacity"], data["current_occupancy"] + noise))
            data["current_occupancy"] = new_occ
            
            # Recalculate wait times based on occupancy
            ratio = new_occ / data["max_capacity"]
            if ratio < 0.4:
                data["congestion_level"] = "Low"
                data["wait_time_minutes"] = max(1, int(ratio * 12))
            elif ratio < 0.75:
                data["congestion_level"] = "Medium"
                data["wait_time_minutes"] = int(ratio * 25)
            else:
                data["congestion_level"] = "High"
                data["wait_time_minutes"] = int(ratio * 35)
                
        return list(self.gates.values())

    def get_incidents(self) -> List[Dict]:
        return self.incidents

    def create_incident(self, incident_data: Dict) -> Dict:
        incident_id = f"INC-{random.randint(1000, 9999)}"
        new_incident = {
            "id": incident_id,
            "title": incident_data["title"],
            "description": incident_data["description"],
            "zone": incident_data["zone"],
            "severity": incident_data["severity"],
            "status": "Open",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.incidents.insert(0, new_incident)
        return new_incident

    def resolve_incident(self, incident_id: str) -> bool:
        for idx, inc in enumerate(self.incidents):
            if inc["id"] == incident_id:
                self.incidents[idx]["status"] = "Resolved"
                return True
        return False

    def add_sustainability_stats(self, username: str, points: int, co2: float):
        self.sustainability_points += points
        self.co2_saved += co2
        
        # Check if user is in leaderboard, update or add
        found = False
        for entry in self.leaderboard:
            if entry["username"] == username:
                entry["points"] += points
                entry["co2_saved_kg"] += co2
                found = True
                break
        
        if not found:
            self.leaderboard.append({
                "username": username,
                "points": points,
                "co2_saved_kg": co2
            })
            
        # Re-sort leaderboard
        self.leaderboard.sort(key=lambda x: x["points"], reverse=True)

    def get_leaderboard(self) -> List[Dict]:
        return self.leaderboard

simulator = StadiumSimulator()
