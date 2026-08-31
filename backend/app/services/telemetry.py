import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("nexusdev_telemetry")

class AgentTelemetryLogger:
    """
    OpenTelemetry-compliant Telemetry & Audit Logger
    Outputs structured JSON logs for Google Cloud Logging & Vertex AI Telemetry,
    visualizing multi-agent reasoning chains, prompt tokens, tool calls, and timing.
    """

    def __init__(self):
        self._trace_buffer: List[Dict[str, Any]] = []
        try:
            import google.cloud.logging
            from app.config import settings
            gcp_proj = getattr(settings, "gcp_project_id", "gen-lang-client-0856296985")
            gcp_client = google.cloud.logging.Client(project=gcp_proj)
            gcp_client.setup_logging()
            logger.info(f"Connected Google Cloud Logging handler for project: {gcp_proj}")
        except Exception as e:
            logger.debug(f"Google Cloud Logging handler setup skipped: {e}")

    def log_agent_event(
        self,
        agent_name: str,
        event_type: str,
        pipeline_id: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format and log an OpenTelemetry structured audit log entry."""
        active_trace_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        span_id = f"span-{uuid.uuid4().hex[:8]}"

        log_payload = {
            "telemetry_version": "1.0-OTel",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "NexusDev-AI-Agent-Fleet",
            "trace_id": active_trace_id,
            "span_id": span_id,
            "agent_name": agent_name,
            "event_type": event_type,  # e.g., 'EPIC_DECOMPOSITION', 'CODE_GENERATION', 'SECURITY_AUDIT', 'GITOPS_COMMIT', 'QA_DEPLOYMENT'
            "pipeline_id": pipeline_id,
            "summary": summary,
            "duration_ms": duration_ms or 0.0,
            "details": details or {}
        }
        
        # Buffer trace span for REST API inspection
        self._trace_buffer.append(log_payload)
        if len(self._trace_buffer) > 100:
            self._trace_buffer.pop(0)

        # Log as single-line JSON string for Cloud Logging ingestion
        json_output = json.dumps(log_payload)
        logger.info(json_output)
        return log_payload

    def get_recent_traces(self) -> List[Dict[str, Any]]:
        """Return array of buffered OpenTelemetry trace spans."""
        return list(self._trace_buffer)

    def clear_traces(self):
        """Clear trace buffer."""
        self._trace_buffer.clear()

telemetry = AgentTelemetryLogger()
