import os
import sys
import logging
from pathlib import Path

# Auto-add backend directory to sys.path so 'import app' works from anywhere
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.schemas.decomposition_schemas import DecompositionResult, HumanFeedbackRequest
from app.agents.decomposer_agent import decomposer_agent
from app.agents.developer_agent import developer_agent
from app.agents.security_agent import security_agent
from app.agents.git_agent import git_agent
from app.agents.release_agent import release_agent
from app.services.jira_service import jira_service
from app.services.memory_bank import memory_bank
from app.services.approval_service import approval_service
from app.routes.approval_routes import router as approval_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexusdev_backend")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="NexusDev AI - 5-Agent Enterprise SDLC Fleet Backend",
    description="5-Agent Software Engineering Network built on Google ADK, Gemini 3.6 Flash / 3.5 Pro, and Salesforce DX.",
    version="2.0.0"
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
    return {"message": "NexusDev AI 5-Agent Fleet Server is running. Frontend UI not found."}

from app.mcp.mcp_client import mcp_client

from app.services.telemetry import telemetry

from app.services.pubsub_cron_service import pubsub_cron_service
from app.services.eval_service import eval_service
from app.services.optimizer_service import optimizer_service

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "NexusDev AI 5-Agent Fleet",
        "mcp_enabled": True,
        "adk_afc_enabled": True,
        "telemetry_enabled": True,
        "pubsub_enabled": True,
        "cron_enabled": True,
        "eval_engine_enabled": True,
        "email_notifications_enabled": True,
        "adk_optimizer_enabled": True,
        "approver_emails": {
            "stage_1_decomposer": settings.decomposer_approver_email,
            "stage_2_developer": settings.developer_approver_email,
            "stage_3_release": settings.release_approver_email
        },
        "active_agents": [
            "1. PM Decomposer Agent (Gemini 3.6 Flash)",
            "2. Salesforce Developer Agent (Gemini 3.5 Pro)",
            "3. Security & Governance Agent (Gemma 2 / Model Armor)",
            "4. GitOps & Version Control Agent (Gemini 3.6 Flash)",
            "5. Enterprise Release Agent (Gemini 3.6 Flash)"
        ],
        "gcp_project": settings.gcp_project_id,
        "jira_domain": settings.jira_domain
    }

@app.get("/api/v1/mcp/tools")
def list_mcp_tools():
    """
    List all active Model Context Protocol (MCP) tools registered across Jira, Salesforce DX, and Git servers.
    """
    tools = mcp_client.list_all_mcp_tools()
    return {
        "mcp_protocol": "Model Context Protocol v1.0",
        "total_tools": len(tools),
        "tools": tools
    }

@app.get("/api/v1/telemetry/traces")
def get_telemetry_traces():
    """
    Retrieve live OpenTelemetry-compliant trace spans and active pipeline session state.
    """
    traces = telemetry.get_recent_traces()
    active_session = memory_bank.get_latest_active_session()
    
    active_approval = None
    from app.services.approval_service import APPROVAL_TOKENS
    for tok, data in reversed(list(APPROVAL_TOKENS.items())):
        if data.get("status") == "PENDING" and tok != "tok-demo-123":
            active_approval = data
            break

    return {
        "telemetry_standard": "OpenTelemetry v1.0 / Google Cloud Trace",
        "total_spans": len(traces),
        "traces": traces,
        "active_session": active_session,
        "active_approval": active_approval
    }

@app.post("/api/v1/pubsub/events")
def handle_pubsub_event(envelope: dict = Body(...)):
    """
    Google Cloud Pub/Sub HTTP Push Ingestion Endpoint.
    Receives real-time asynchronous Pub/Sub topic events and triggers the Root PM Decomposer Agent.
    """
    logger.info("Inbound Google Cloud Pub/Sub Push Notification received.")
    return pubsub_cron_service.handle_pubsub_event(envelope)

@app.post("/api/v1/cron/nightly-audit")
def trigger_cron_nightly_audit():
    """
    Google Cloud Scheduler Cron Endpoint (Schedule: 0 0 * * *).
    Triggers recurring nightly governance and security audit across connected Salesforce metadata.
    """
    logger.info("Inbound Google Cloud Scheduler Cron Trigger received (0 0 * * *).")
    return pubsub_cron_service.execute_cron_nightly_audit()

@app.get("/api/v1/eval/benchmark")
def get_eval_benchmark():
    """
    Execute quantitative LLM-as-a-Judge Evaluation Benchmark suite across the 5 ADK agents.
    Returns metrics for self-correction recovery rate, security compliance index, and latency.
    """
    logger.info("Executing Evaluation Benchmark API trigger...")
    return eval_service.run_evaluation_benchmark()

@app.get("/api/v1/adk/optimize")
def get_adk_optimization():
    """
    Retrieve Google ADK 2.0 Fleet Optimization profile and hyperparameter metrics.
    Returns agent temperature profiles, AFC token savings, schema validation, and fallback routing configs.
    """
    logger.info("Executing ADK Fleet Optimization API trigger...")
    return optimizer_service.get_adk_optimization_profile()

@app.post("/api/v1/git/commit-and-pr")
def trigger_git_agent(task_title: str = Body("Student Application Form", embed=True), branch_name: str = Body("feature/SCRUM-1-student-app", embed=True)):
    """
    Trigger GitOps Agent (Google ADK / Gemini 3.6 Flash):
    Generates AI conventional commit messages, pushes feature branch, and creates PR summary.
    """
    logger.info(f"Triggering GitOps Agent for task: '{task_title}' on branch '{branch_name}'...")
    res = git_agent.commit_and_generate_pr(task_title=task_title, branch_name=branch_name)
    return res

@app.post("/api/v1/release/deploy-and-notes")
def trigger_release_agent(target_org: str = Body("qa-org", embed=True), stage_name: str = Body("QA_TESTING_ORG", embed=True)):
    """
    Trigger Enterprise Release Agent (Google ADK / Gemini 3.6 Flash):
    Executes pre-flight checks, metadata deployment, and generates Enterprise Release Notes.
    """
    logger.info(f"Triggering Enterprise Release Agent for target org '{target_org}'...")
    res = release_agent.validate_and_deploy_release(target_org=target_org, stage_name=stage_name)
    return res

@app.post("/api/v1/epics/decompose", response_model=DecompositionResult)
async def decompose_jira_epic(request: Request):
    """
    Trigger PM Decomposer Agent (Gemini 3.6 Flash):
    Supports both direct API calls ({"epic_key": "SCRUM-82"}) and native Jira Webhooks ({"issue": {"key": "SCRUM-82"}}).
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    
    # Check if incoming webhook is a Jira event
    webhook_event = payload.get("webhookEvent")
    if webhook_event and webhook_event != "jira:issue_created":
        logger.info(f"Ignoring non-creation Jira webhook event: '{webhook_event}' for key {payload.get('issue', {}).get('key')}")
        return DecompositionResult(
            epic_key=payload.get("issue", {}).get("key", "IGNORED"),
            epic_summary="Ignored Non-Creation Event",
            architectural_overview="Non-creation webhook event filtered.",
            tasks=[],
            approval_token="NONE"
        )

    # Check if incoming webhook is for a non-Epic issue (e.g. Story/Task created by the agent)
    issue_type = payload.get("issue", {}).get("fields", {}).get("issuetype", {}).get("name")
    if issue_type and issue_type != "Epic":
        logger.info(f"Ignoring Jira webhook for non-Epic issue type: '{issue_type}' (Key: {payload.get('issue', {}).get('key')})")
        return DecompositionResult(
            epic_key=payload.get("issue", {}).get("key", "IGNORED"),
            epic_summary="Ignored Non-Epic Issue Event",
            architectural_overview="Non-Epic webhook event filtered.",
            tasks=[],
            approval_token="NONE"
        )

    epic_key = payload.get("epic_key") or payload.get("issue", {}).get("key") or "SCRUM-82"
    human_feedback = payload.get("human_feedback")
    logger.info(f"Received decomposition request for Epic: {epic_key} (Issue Type: {issue_type or 'Direct/API'})")
    
    # Check if Epic has ALREADY been processed in Memory Bank to prevent duplicate/delayed decomposition
    if memory_bank.has_epic_been_processed(epic_key) and not human_feedback:
        logger.info(f"Epic '{epic_key}' has ALREADY been processed in Memory Bank. Ignoring retry/delayed webhook trigger.")
        latest_session = memory_bank.get_latest_active_session()
        return DecompositionResult(
            epic_key=epic_key,
            epic_summary="Already Processed",
            architectural_overview="Epic already decomposed and active in pipeline.",
            tasks=[],
            approval_token="NONE"
        )
    
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
