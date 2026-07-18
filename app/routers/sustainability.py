"""
API Router for sustainability metrics, gamified points, and trash analysis.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import WasteAnalysisRequest, WasteAnalysisResponse, SustainabilityLeaderboardResponse, LeaderboardEntry
from app.services.groq_service import groq_service
from app.services.simulator import simulator
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sustainability", tags=["Sustainability & Eco-Impact Tracker"])

@router.post("/analyze", response_model=WasteAnalysisResponse)
async def analyze_waste_sorting(payload: WasteAnalysisRequest):
    """
    Simulates scanning/taking a photo of trash. Calls GenAI (or simulation context) 
    to output sorting instructions, target bin class (recycle, compost, landfill), 
    CO2 offsets, and gamified reward points.
    """
    try:
        waste_data = groq_service.analyze_waste_item(payload.item_id)
        return WasteAnalysisResponse(
            item_name=waste_data["item_name"],
            target_bin=waste_data["target_bin"],
            co2_saved_kg=waste_data["co2_saved_kg"],
            points_awarded=waste_data["points_awarded"],
            sorting_instruction=waste_data["sorting_instruction"],
            sustainability_tip=waste_data["sustainability_tip"]
        )
    except Exception as e:
        logger.error(f"Error classifying waste items: {e}")
        raise HTTPException(status_code=500, detail="Failed to run waste carbon classification.")

@router.get("/leaderboard", response_model=SustainabilityLeaderboardResponse)
async def get_leaderboard_standings():
    """
    Retrieves the crowd carbon-savings leaderboard standings.
    """
    try:
        raw_leaderboard = simulator.get_leaderboard()
        entries = [
            LeaderboardEntry(
                username=entry["username"],
                points=entry["points"],
                co2_saved_kg=entry["co2_saved_kg"]
            )
            for entry in raw_leaderboard
        ]
        return SustainabilityLeaderboardResponse(leaderboard=entries)
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve eco-leaderboard.")

@router.post("/add-points")
async def register_eco_action(username: str, points: int, co2_saved_kg: float):
    """
    Registers an individual user's recycling event to scale overall stadium environmental impact.
    """
    try:
        if not username or len(username) < 3:
            raise HTTPException(status_code=400, detail="Invalid username length.")
        simulator.add_sustainability_stats(username, points, co2_saved_kg)
        return {
            "message": "Eco-points recorded successfully!",
            "username": username,
            "current_stadium_points": simulator.sustainability_points,
            "current_stadium_co2_saved": simulator.co2_saved
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording eco points: {e}")
        raise HTTPException(status_code=500, detail="Failed to update sustainability metrics.")
