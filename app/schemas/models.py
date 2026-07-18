"""
Pydantic data transfer schemas validating API request/response structures.
"""
from enum import Enum
import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class UserRole(str, Enum):
    """Supported roles for the ArenaSync AI system."""
    FAN = "fan"
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"

class LanguageCode(str, Enum):
    """Supported language locales."""
    EN = "en"
    ES = "es"
    FR = "fr"

class ChatMessage(BaseModel):
    """Schema representing a single message within the chat history."""
    role: str = Field(..., description="Role of the message author: 'user' or 'model'")
    content: str = Field(..., min_length=1, max_length=1000, description="Content of the message")

    model_config = {
        "extra": "forbid"
    }

class AssistantRequest(BaseModel):
    """Request validation schema for conversational AI copilot."""
    user_role: UserRole = Field(UserRole.FAN, description="Role context: 'fan', 'volunteer', or 'organizer'")
    message: str = Field(..., min_length=1, description="User's query")
    history: List[ChatMessage] = Field(default_factory=list, description="Chat message history for conversational state")
    language: LanguageCode = Field(LanguageCode.EN, description="Preferred output language: 'en', 'es', or 'fr'")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("message")
    @classmethod
    def sanitize_message_input(cls, val: str) -> str:
        """Strip control characters and restrict the message length."""
        sanitized = "".join(ch for ch in val if ord(ch) >= 32 or ch in "\n\r\t")
        sanitized = sanitized.strip()
        if not sanitized:
            raise ValueError("Message cannot be empty or contain only control characters.")
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
        return sanitized

class AssistantResponse(BaseModel):
    """Response payload matching conversational query endpoints."""
    response: str
    detected_language: str
    suggested_actions: List[str] = []

    model_config = {
        "extra": "ignore"
    }

class WasteAnalysisRequest(BaseModel):
    """Request payload containing waste scanner classification tags."""
    item_id: str = Field(..., min_length=1, max_length=50, description="Identifier of the waste item to analyze")

    model_config = {
        "extra": "forbid"
    }

class WasteAnalysisResponse(BaseModel):
    """Result structure outputting waste categorization metrics."""
    item_name: str
    target_bin: str = Field(..., description="Recycle, Compost, or Landfill")
    co2_saved_kg: float
    points_awarded: int
    sorting_instruction: str
    sustainability_tip: str

class LeaderboardEntry(BaseModel):
    """Individual high score entry on the global eco-board."""
    username: str
    points: int
    co2_saved_kg: float

class SustainabilityLeaderboardResponse(BaseModel):
    """Leaderboard wrapper list."""
    leaderboard: List[LeaderboardEntry]

class IncidentCreate(BaseModel):
    """Request payload to create a new ticket command incident log."""
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    zone: str = Field(..., description="Stadium zone ID e.g., 'Gate A', 'Section 109'")
    severity: str = Field("Medium", description="Low, Medium, or High")

    model_config = {
        "extra": "forbid"
    }

    @field_validator("zone")
    @classmethod
    def validate_zone_id(cls, value: str) -> str:
        """Enforces that the zone matches standard MetLife locations."""
        value_clean = value.strip()
        pattern = r"^(Gate [A-D]( \([A-Za-z\s]+\))?|Section \d{3}(\s+[A-Za-z\s]+)?|Suite \d{3}|Lot [A-G]|Verizon VIP Entrance|HCL Tech Suite Entrance)$"
        if not re.match(pattern, value_clean, re.IGNORECASE):
            raise ValueError(f"Unknown or invalid zone ID: '{value_clean}'. Must match standard stadium zone structures.")
        return value_clean

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        """Enforces that only Low, Medium, and High are accepted severity ratings."""
        if value not in ("Low", "Medium", "High"):
            raise ValueError("Severity must be Low, Medium, or High")
        return value

class Incident(BaseModel):
    """Stateful record representing an operational ticket."""
    id: str
    title: str
    description: str
    zone: str
    severity: str
    status: str = "Open"
    timestamp: str

class IncidentResolutionResponse(BaseModel):
    """Drafted response plan output including multi-language public safety warning declarations."""
    incident_id: str
    status: str
    response_plan: str
    announcements: Dict[str, str] = Field(..., description="Language-specific drafted public announcements (en, es, fr)")
    assigned_tasks: List[str] = Field(..., description="Tasks automatically dispatched to volunteers")

class CrowdStatusResponse(BaseModel):
    """Congestion status wrapper for MetLife Stadium gates."""
    gate: str
    current_occupancy: int
    max_capacity: int
    wait_time_minutes: int
    congestion_level: str
    recommended_action: str
