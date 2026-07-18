"""
API Router for the AI assistant chatbot, handling RAG context injection and multi-agent translation.
"""
import time
import logging
from collections import defaultdict
from typing import Dict
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.schemas.models import AssistantRequest, AssistantResponse
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

class TokenBucketRateLimiter:
    """In-memory per-IP token-bucket rate limiter."""
    def __init__(self, rate: float, capacity: float):
        self.rate = rate          # tokens replenished per second
        self.capacity = capacity  # burst capacity
        self.buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"tokens": float(capacity), "last_update": time.time()}
        )

    def consume(self, ip: str) -> bool:
        """Consumes a single token. Returns True if accepted, False if rate-limited."""
        now = time.time()
        bucket = self.buckets[ip]
        elapsed = now - bucket["last_update"]
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.rate)
        bucket["last_update"] = now
        
        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True
        return False

# Limit to 1 request per 2 seconds, burst up to 5 tokens per IP
rate_limiter = TokenBucketRateLimiter(rate=0.5, capacity=5.0)

@router.post("/chat")
async def chat_assistant(payload: AssistantRequest, request: Request):
    """
    Exposes role-specific multilingual conversational GenAI interface.
    Integrates with RAG grounding store automatically.
    """
    ip = request.client.host if request.client else "unknown"
    if not rate_limiter.consume(ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please wait before querying again."},
            headers={"Retry-After": "2"}
        )
        
    try:
        response_data = groq_service.get_assistant_response(
            role=payload.user_role.value,
            query=payload.message,
            history=[h.model_dump() for h in payload.history],
            language=payload.language.value
        )
        
        return response_data
    except Exception as e:
        logger.error(f"Error in chat assistant router: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant Service Error: {str(e)}"
        )
