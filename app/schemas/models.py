"""
Pydantic data transfer schemas validating API request/response structures.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message author: 'user' or 'model'")
    content: str = Field(..., description="Content of the message")

class AssistantRequest(BaseModel):
    user_role: str = Field("fan", description="Role context: 'fan', 'volunteer', or 'organizer'")
    message: str = Field(..., max_length=1000, description="User's query")
    history: List[ChatMessage] = Field(default_factory=list, description="Chat message history for conversational state")
    language: str = Field("en", description="Preferred output language: 'en', 'es', or 'fr'")

class AssistantResponse(BaseModel):
    response: str
    detected_language: str
    suggested_actions: List[str] = []

class WasteAnalysisRequest(BaseModel):
    item_id: str = Field(..., description="Identifier of the waste item to analyze")

class WasteAnalysisResponse(BaseModel):
    item_name: str
    target_bin: str = Field(..., description="Recycle, Compost, or Landfill")
    co2_saved_kg: float
    points_awarded: int
    sorting_instruction: str
    sustainability_tip: str

class LeaderboardEntry(BaseModel):
    username: str
    points: int
    co2_saved_kg: float

class SustainabilityLeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardEntry]

class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    zone: str = Field(..., description="Stadium zone e.g., 'Zone A', 'Gate 3', 'Section 114'")
    severity: str = Field("Medium", description="Low, Medium, or High")

class Incident(BaseModel):
    id: str
    title: str
    description: str
    zone: str
    severity: str
    status: str = "Open"
    timestamp: str

class IncidentResolutionResponse(BaseModel):
    incident_id: str
    status: str
    response_plan: str
    announcements: Dict[str, str] = Field(..., description="Language-specific drafted public announcements (en, es, fr)")
    assigned_tasks: List[str] = Field(..., description="Tasks automatically dispatched to volunteers")

class CrowdStatusResponse(BaseModel):
    gate: str
    current_occupancy: int
    max_capacity: int
    wait_time_minutes: int
    congestion_level: str  # Low, Medium, High
    recommended_action: str
