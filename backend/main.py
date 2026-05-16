import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.services import InMemorySessionService, InMemoryMemoryService
from .agent import github_card_agent

app = FastAPI(title="GitHub Dev Card API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
STATIC_DIR = os.path.join(os.getcwd(), "static", "cards")
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files (optional, but we'll use a custom endpoint for serving)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize ADK Services and Runner
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
runner = Runner(
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service
)

class GenerateRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    """Triggers the ADK agent to generate and save a dev card."""
    username = request.username
    session_id = f"session_{username}"
    
    try:
        # Run the agent for the specific user session
        # The agent will automatically call the MCP tools in sequence
        response = await runner.run(
            f"Generate a dev card for {username}",
            session_id=session_id
        )
        
        # Construct the expected file path
        card_path = os.path.join(STATIC_DIR, f"{username}.html")
        
        if not os.path.exists(card_path):
            return {"status": "processing", "message": response}
            
        with open(card_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        return {
            "username": username,
            "card_url": f"/card/{username}",
            "html": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    """Serves a saved HTML dev card."""
    file_path = os.path.join(STATIC_DIR, f"{username}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Card not found")

@app.get("/health")
async def health_check():
    """Cloud Run health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
