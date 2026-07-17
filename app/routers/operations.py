from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.schemas.models import CrowdStatusResponse, Incident, IncidentCreate, IncidentResolutionResponse
from app.services.simulator import simulator
from app.services.groq_service import groq_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/operations", tags=["Operations & Crowd Management"])

@router.get("/gates", response_model=List[CrowdStatusResponse])
async def get_gates_status():
    """
    Returns simulated real-time crowd congestion indicators at stadium gates.
    """
    try:
        return simulator.get_gates()
    except Exception as e:
        logger.error(f"Error fetching gates status: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve stadium gate status.")

@router.get("/incidents", response_model=List[Incident])
async def get_open_incidents():
    """
    Retrieves the queue of currently open operational issues at the stadium.
    """
    try:
        return [inc for inc in simulator.get_incidents() if inc["status"] == "Open"]
    except Exception as e:
        logger.error(f"Error fetching open incidents: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch open incident list.")

@router.post("/incidents", response_model=Incident)
async def create_new_incident(payload: IncidentCreate):
    """
    Allows organizers or volunteers to log a new stadium operations ticket.
    """
    try:
        new_inc = simulator.create_incident(payload.model_dump())
        return new_inc
    except Exception as e:
        logger.error(f"Error logging incident: {e}")
        raise HTTPException(status_code=500, detail="Failed to create incident report.")

@router.post("/incidents/{incident_id}/resolve")
async def resolve_active_incident(incident_id: str = Path(..., description="ID of incident ticket")):
    """
    Marks an operational incident as closed.
    """
    try:
        success = simulator.resolve_incident(incident_id)
        if not success:
            raise HTTPException(status_code=404, detail="Incident ticket not found.")
        return {"message": "Incident marked as Resolved successfully.", "incident_id": incident_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to close incident ticket.")

@router.post("/incidents/{incident_id}/ai-plan", response_model=IncidentResolutionResponse)
async def generate_resolution_plan(incident_id: str = Path(..., description="ID of incident ticket")):
    """
    GenAI-powered decision support: drafts resolution strategies, multi-language emergency declarations,
    and volunteer action items for the specific incident.
    """
    try:
        # 1. Fetch incident detail
        incident = next((inc for inc in simulator.get_incidents() if inc["id"] == incident_id), None)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident ticket not found.")
            
        # 2. Ask Groq Service to draft operational plan
        plan_data = groq_service.generate_incident_response_plan(incident)
        
        return IncidentResolutionResponse(
            incident_id=incident_id,
            status=incident["status"],
            response_plan=plan_data["response_plan"],
            announcements=plan_data["announcements"],
            assigned_tasks=plan_data["assigned_tasks"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI plan for {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to synthesize GenAI operations plan.")
