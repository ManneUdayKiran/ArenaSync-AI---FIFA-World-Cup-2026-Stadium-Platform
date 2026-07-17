import os
import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers import assistant, operations, sustainability
from app.services.groq_service import groq_service

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GenAI-enabled Stadium Operations & Fan Experience Platform for FIFA World Cup 2026."
)

# CORS Setup for secure communications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define directory structures
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Ensure static directories exist
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount Static Files & Setup HTML Templates
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Register Routers
app.include_router(assistant.router)
app.include_router(operations.router)
app.include_router(sustainability.router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware for efficiency logging and tracking server execution bottlenecks.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/", response_class=HTMLResponse)
async def serve_home_page(request: Request):
    """
    Serves the primary ArenaSync single-page application interface.
    """
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "stadium_name": settings.STADIUM_NAME,
            "gemini_mode": "Groq Cloud (gpt-oss-120b)" if groq_service.is_active else "Intelligent Fallback Simulation"
        }
    )

@app.get("/api/health")
async def check_api_health():
    """
    General service status check containing diagnostics configurations.
    """
    return {
        "status": "online",
        "stadium": settings.STADIUM_NAME,
        "groq_sdk_enabled": groq_service.is_active,
        "api_key_configured": bool(settings.GROQ_API_KEY),
        "version": settings.VERSION
    }
