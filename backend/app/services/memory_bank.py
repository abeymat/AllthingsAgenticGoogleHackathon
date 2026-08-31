import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from app.config import settings

logger = logging.getLogger(__name__)

import json
from pathlib import Path

CACHE_FILE = Path(__file__).resolve().parent.parent.parent.parent / "scratch" / "active_session_cache.json"

class MemoryBankService:
    """
    Firestore Memory Bank Service
    Maintains persistent, cross-session agent state, session memory, and pipeline history
    across asynchronous human approval wait cycles.
    """

    def __init__(self):
        self.project_id = settings.gcp_project_id
        self._db = None
        self._mock_memory_store: Dict[str, Dict[str, Any]] = {}
        self._load_disk_cache()

    def _load_disk_cache(self):
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r") as f:
                    self._mock_memory_store = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load session cache: {e}")

    def _save_disk_cache(self):
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump(self._mock_memory_store, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save session cache: {e}")

    @property
    def db(self):
        if not self._db and self.project_id:
            try:
                logger.info(f"Connecting to Google Cloud Firestore in project '{self.project_id}'...")
                self._db = firestore.Client(project=self.project_id)
            except Exception as e:
                logger.warning(f"Firestore connection unavailable ({e}). Using in-memory fallback store for local dev.")
                self._db = None
        return self._db

    def create_pipeline_session(self, epic_key: str, epic_summary: str) -> str:
        """Initialize a new pipeline execution session."""
        pipeline_id = f"pipe-{uuid.uuid4().hex[:8]}"
        session_data = {
            "pipeline_id": pipeline_id,
            "epic_key": epic_key,
            "epic_summary": epic_summary,
            "current_status": "CREATED",
            "current_stage": "INITIATED",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "decomposition": None,
            "development_artifacts": [],
            "approval_tokens": {},
            "audit_trail": [{
                "timestamp": datetime.utcnow().isoformat(),
                "event": "Pipeline Created",
                "stage": "INITIATED"
            }]
        }

        self._mock_memory_store[pipeline_id] = session_data
        self._save_disk_cache()

        if self.db:
            try:
                self.db.collection("pipeline_sessions").document(pipeline_id).set(session_data)
            except Exception as e:
                logger.error(f"Firestore write error: {e}")

        logger.info(f"Created Pipeline Session: {pipeline_id} for Epic {epic_key}")
        return pipeline_id

    def update_pipeline_state(self, pipeline_id: str, status: str, stage: str, payload_update: Optional[Dict[str, Any]] = None):
        """Update pipeline status and log audit event in Memory Bank."""
        now = datetime.utcnow().isoformat()
        audit_event = {
            "timestamp": now,
            "event": f"State updated to {status}",
            "stage": stage
        }

        self._update_mock_store(pipeline_id, status, stage, payload_update, audit_event)
        self._save_disk_cache()

        if self.db:
            try:
                doc_ref = self.db.collection("pipeline_sessions").document(pipeline_id)
                update_dict = {
                    "current_status": status,
                    "current_stage": stage,
                    "updated_at": now,
                    "audit_trail": firestore.ArrayUnion([audit_event])
                }
                if payload_update:
                    update_dict.update(payload_update)
                doc_ref.update(update_dict)
            except Exception as e:
                logger.error(f"Firestore update error: {e}")

        logger.info(f"Pipeline {pipeline_id} state updated -> Status: {status}, Stage: {stage}")

    def get_pipeline_session(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full pipeline session state from Memory Bank."""
        if self.db:
            try:
                doc = self.db.collection("pipeline_sessions").document(pipeline_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore read error: {e}")
        return self._mock_memory_store.get(pipeline_id)

    def get_latest_active_session(self) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent active pipeline session from Memory Bank."""
        if self._mock_memory_store:
            latest_id = list(self._mock_memory_store.keys())[-1]
            return self._mock_memory_store[latest_id]
        return None

    def has_epic_been_processed(self, epic_key: str) -> bool:
        """Check if an epic key has already been processed in any pipeline session."""
        for session in self._mock_memory_store.values():
            if session.get("epic_key") == epic_key:
                return True
        return False

    def _update_mock_store(self, pipeline_id: str, status: str, stage: str, payload_update: Optional[Dict[str, Any]], audit_event: Dict[str, Any]):
        session = self._mock_memory_store.get(pipeline_id, {})
        session["current_status"] = status
        session["current_stage"] = stage
        session["updated_at"] = datetime.utcnow().isoformat()
        if "audit_trail" not in session:
            session["audit_trail"] = []
        session["audit_trail"].append(audit_event)
        if payload_update:
            session.update(payload_update)
        self._mock_memory_store[pipeline_id] = session

memory_bank = MemoryBankService()
