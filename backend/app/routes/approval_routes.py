import logging
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from app.services.approval_service import approval_service
from app.services.memory_bank import memory_bank

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/approve", tags=["Human Approval Engine"])

@router.get("/view", response_class=HTMLResponse)
def render_approval_portal(token: str = Query(...)):
    """Render interactive HTML Human Approval Portal for magic links."""
    details = approval_service.get_token_details(token)
    if not details:
        return HTMLResponse(content="<h2>Invalid or Expired Approval Link</h2>", status_code=404)

    pipeline_id = details["pipeline_id"]
    stage = details["stage"]
    pipeline_state = memory_bank.get_pipeline_session(pipeline_id) or {}
    meta = details.get("metadata", {})

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NexusDev AI - Human Approval Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
            .card {{ max-width: 700px; margin: 30px auto; background-color: #1e293b; border-radius: 12px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }}
            h1 {{ color: #38bdf8; font-size: 24px; margin-top: 0; }}
            .badge {{ display: inline-block; background-color: #0284c7; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; text-transform: uppercase; margin-bottom: 15px; }}
            .content-box {{ background-color: #090d16; border: 1px solid #334155; border-radius: 8px; padding: 15px; font-family: monospace; white-space: pre-wrap; font-size: 13px; max-height: 250px; overflow-y: auto; color: #a5f3fc; margin-bottom: 20px; }}
            textarea {{ width: 100%; height: 80px; background-color: #090d16; border: 1px solid #475569; border-radius: 6px; color: white; padding: 10px; font-family: inherit; font-size: 14px; margin-bottom: 15px; box-sizing: border-box; }}
            .btn-group {{ display: flex; gap: 10px; }}
            button {{ flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 15px; transition: background-color 0.2s; }}
            .btn-approve {{ background-color: #22c55e; color: white; }}
            .btn-approve:hover {{ background-color: #16a34a; }}
            .btn-modify {{ background-color: #eab308; color: black; }}
            .btn-modify:hover {{ background-color: #ca8a04; }}
            .btn-reject {{ background-color: #ef4444; color: white; }}
            .btn-reject:hover {{ background-color: #dc2626; }}
            #status-msg {{ margin-top: 15px; font-weight: 600; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">Stage: {stage} Approval Checkpoint</span>
            <h1>NexusDev AI - Human Sign-off</h1>
            <p><strong>Pipeline ID:</strong> {pipeline_id}</p>
            <p><strong>Epic Summary:</strong> {pipeline_state.get('epic_summary', 'Salesforce SDLC Task')}</p>
            
            <h3>Artifact for Review:</h3>
            <div class="content-box">{meta.get('preview_text', 'Artifact review content ready.')}</div>

            <h3>Request Modifications (Optional Feedback):</h3>
            <textarea id="feedbackText" placeholder="Type comments or requested modifications for the agent fleet..."></textarea>

            <div class="btn-group">
                <button class="btn-approve" onclick="submitDecision('approve')">✓ Approve</button>
                <button class="btn-modify" onclick="submitDecision('request_changes')">✎ Request Changes</button>
                <button class="btn-reject" onclick="submitDecision('reject')">✕ Reject</button>
            </div>

            <div id="status-msg"></div>
        </div>

        <script>
            async function submitDecision(action) {{
                const feedback = document.getElementById('feedbackText').value;
                const statusDiv = document.getElementById('status-msg');
                statusDiv.innerText = "Processing decision...";
                try {{
                    const response = await fetch('/api/v1/approve/action', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token: '{token}', action: action, feedback_text: feedback }})
                    }});
                    const data = await response.json();
                    if (response.ok) {{
                        statusDiv.style.color = "#4ade80";
                        statusDiv.innerText = data.message;
                    }} else {{
                        statusDiv.style.color = "#f87171";
                        statusDiv.innerText = "Error: " + (data.detail || "Submission failed");
                    }}
                }} catch (e) {{
                    statusDiv.style.color = "#f87171";
                    statusDiv.innerText = "Network error submitting approval decision.";
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/action")
def submit_approval_action(
    token: str = Body(..., embed=True),
    action: str = Body(..., embed=True),
    feedback_text: str = Body(None, embed=True)
):
    """Process approval decision payload from web portal or API."""
    try:
        res = approval_service.process_approval_decision(token=token, action=action, feedback_text=feedback_text)
        return res
    except Exception as e:
        logger.error(f"Approval action error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
