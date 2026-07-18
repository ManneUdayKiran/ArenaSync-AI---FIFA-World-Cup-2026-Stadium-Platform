"""
API Router for the AI assistant chatbot, handling RAG context injection and multi-agent translation.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import AssistantRequest, AssistantResponse
from app.services.groq_service import groq_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

@router.post("/chat", response_model=AssistantResponse)
async def chat_assistant(payload: AssistantRequest):
    """
    Exposes role-specific multilingual conversational GenAI interface.
    Integrates with RAG grounding store automatically.
    """
    try:
        # Convert history format
        formatted_history = []
        for msg in payload.history:
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })
            
        # Get AI response
        ai_payload = groq_service.get_assistant_response(
            role=payload.user_role,
            query=payload.message,
            history=formatted_history,
            language=payload.language
        )
        
        return AssistantResponse(
            response=ai_payload["response"],
            detected_language=ai_payload["detected_language"],
            suggested_actions=ai_payload["suggested_actions"]
        )
    except Exception as e:
        logger.error(f"Error handling assistant chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error executing assistant query.")
