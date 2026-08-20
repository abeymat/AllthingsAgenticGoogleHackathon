import os
import sys
import logging
from pathlib import Path

# Auto-add backend directory to sys.path so 'import app' works from anywhere
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.schemas.decomposition_schemas import DecompositionResult, HumanFeedbackRequest
from app.agents.decomposer_agent import decomposer_agent
from app.agents.developer_agent import developer_agent
from app.agents.security_agent import security_agent
from app.services.jira_service import jira_service
from app.services.memory_bank import memory_bank
from app.services.approval_service import approval_service
from app.routes.approval_routes import router as approval_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexusdev_backend")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="NexusDev AI - Enterprise Agentic SDLC Backend",
    description="Multi-Agent Software Engineering Network built on Google ADK, Gemini 3.5 Pro, and Salesforce DX.",
    version="1.0.0"
)

# Enable CORS for local Web Dashboard UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Approval Router
app.include_router(approval_router)

@app.get("/")
def serve_dashboard():
    """Serve the Web Control Center Dashboard UI."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "NexusDev AI API Server is running. Frontend UI not found."}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "NexusDev AI Agent Fleet",
        "gcp_project": settings.gcp_project_id,
        "jira_domain": settings.jira_domain
    }

@app.post("/api/v1/epics/decompose", response_model=DecompositionResult)
def decompose_jira_epic(epic_key: str = Body(..., embed=True), human_feedback: str = Body(None, embed=True)):
    """
    Trigger PM Decomposer Agent (Gemini 3.6 Flash):
    1. Decomposes Jira Epic into technical User Stories & Tasks.
    2. Automatically pushes the created User Stories to Jira under project key SCRUM.
    3. Initializes Firestore Memory Bank session and Approval Token #1.
    """
    logger.info(f"Received decomposition request for Epic: {epic_key}")
    
    try:
        epic_data = jira_service.get_issue(epic_key)
        summary = epic_data["summary"]
        description = epic_data["description"]
    except Exception:
        logger.warning(f"Could not fetch {epic_key} directly from Jira API. Using default epic context.")
        summary = f"Create Student Application Form & Registration Trigger for {epic_key}"
        description = "As a University PM, I need an automated student application form LWC and Apex controller."

    # 1. Gemini 3.6 Flash Decomposition
    result = decomposer_agent.decompose_epic(
        epic_key=epic_key,
        epic_summary=summary,
        epic_description=description,
        human_feedback=human_feedback
    )

    # 2. Automatically Create Tasks in Jira
    logger.info(f"Creating {len(result.tasks)} decomposed stories in Jira project {settings.jira_project_key}...")
    for t in result.tasks:
        try:
            jira_service.create_story_or_task(
                parent_key=epic_key if "-" in epic_key else None,
                summary=f"[{t.component_type}] {t.title}",
                description=f"{t.description}\nTarget Filename: {t.target_filename}",
                issue_type="Story"
            )
        except Exception as e:
            logger.warning(f"Note on creating Jira story '{t.title}': {e}")

    # 3. Create Memory Bank Session & Approval Token
    pipeline_id = memory_bank.create_pipeline_session(epic_key=epic_key, epic_summary=summary)
    token = approval_service.generate_approval_token(
        pipeline_id=pipeline_id,
        stage="DECOMPOSITION",
        metadata={"preview_text": result.architectural_overview}
    )
    result.approval_token = token

    return result

@app.post("/api/v1/dev/generate-and-test")
def generate_and_test_code(task_spec: dict = Body(...)):
    """
    Trigger Salesforce Developer Agent:
    Generates Apex/LWC code, executes unit tests via SF CLI, and triggers Self-Correction Loop on failure.
    """
    logger.info(f"Triggering Salesforce Developer Agent for: {task_spec.get('title')}")
    result = developer_agent.develop_and_test_with_self_correction(task_spec)
    return result

@app.post("/api/v1/security/audit")
def audit_code_security(code: str = Body(..., embed=True), component_name: str = Body("ApexComponent", embed=True)):
    """
    Trigger Security & Governance Agent (Model Armor / Gemma 2):
    Scans code for SOQL injection, hardcoded credentials, and policy violations.
    """
    logger.info(f"Auditing code security for {component_name}...")
    audit = security_agent.audit_code_security(code, component_name)
    return audit

@app.post("/api/v1/epics/approve")
def handle_human_approval(request: HumanFeedbackRequest):
    """
    Handle Human-in-the-Loop (HITL) approval checkpoint decisions:
    - 'approve': Proceeds to next agent/stage.
    - 'request_changes': Feeds human feedback back into the agent loop.
    - 'reject': Cancels the workflow.
    """
    logger.info(f"Approval Decision for Pipeline {request.pipeline_id} at Stage '{request.stage}': {request.action}")

    if request.action == "approve":
        return {
            "status": "APPROVED",
            "message": f"Stage '{request.stage}' approved! Proceeding to next agent execution stage.",
            "next_stage": "DEVELOPMENT" if request.stage == "DECOMPOSITION" else "STAGING_DEPLOYMENT"
        }
    
    elif request.action == "request_changes":
        logger.info(f"Re-triggering Agent with Feedback: {request.feedback_text}")
        return {
            "status": "MUTATING",
            "message": f"Feedback received for stage '{request.stage}'. Re-invoking agent for mutation.",
            "feedback_text": request.feedback_text
        }
        
    elif request.action == "reject":
        return {
            "status": "REJECTED",
            "message": f"Pipeline {request.pipeline_id} cancelled by human approver."
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid approval action.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
