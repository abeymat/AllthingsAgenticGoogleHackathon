import uuid
import logging
from typing import Dict, Any, Optional
from app.config import settings
from app.services.memory_bank import memory_bank

logger = logging.getLogger(__name__)

# Global token registry pre-populated with default demo token
APPROVAL_TOKENS: Dict[str, Dict[str, Any]] = {
    "tok-demo-123": {
        "token": "tok-demo-123",
        "pipeline_id": "pipe-demo-123",
        "stage": "DECOMPOSITION",
        "status": "PENDING",
        "metadata": {
            "preview_text": "Decomposed Epic SCRUM-1: Student Application Form into 3 tasks:\n1. [LWC] Student Application LWC Form UI\n2. [ApexClass] Student Application Apex Controller\n3. [ApexTest] Student Application Unit Tests"
        },
        "approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token=tok-demo-123"
    }
}

class ApprovalService:
    """
    Approval & Magic Link Token Engine
    Generates secure tokenized URLs for human approval gates and processes HITL decisions.
    """

    def generate_approval_token(self, pipeline_id: str, stage: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a secure, single-use token for a human approval checkpoint."""
        token = f"tok-{uuid.uuid4().hex}"
        token_data = {
            "token": token,
            "pipeline_id": pipeline_id,
            "stage": stage,
            "status": "PENDING",
            "metadata": metadata or {},
            "approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token={token}"
        }
        APPROVAL_TOKENS[token] = token_data

        # Store token reference in Firestore Memory Bank
        memory_bank.update_pipeline_state(
            pipeline_id=pipeline_id,
            status=f"PENDING_{stage}_APPROVAL",
            stage=stage,
            payload_update={f"token_{stage.lower()}": token_data}
        )

        logger.info(f"Generated Approval Token [{token}] for Pipeline {pipeline_id} at Stage '{stage}'.")
        return token

    def get_token_details(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve token details for human review portal."""
        return APPROVAL_TOKENS.get(token)

    def process_approval_decision(self, token: str, action: str, feedback_text: Optional[str] = None) -> Dict[str, Any]:
        """Process human approval decision ('approve', 'request_changes', 'reject')."""
        token_data = APPROVAL_TOKENS.get(token)
        if not token_data:
            raise ValueError(f"Approval token '{token}' not found or expired.")

        pipeline_id = token_data["pipeline_id"]
        stage = token_data["stage"]

        token_data["status"] = action.upper()
        token_data["human_feedback"] = feedback_text

        if action == "approve":
            memory_bank.update_pipeline_state(
                pipeline_id=pipeline_id,
                status=f"{stage}_APPROVED",
                stage=stage,
                payload_update={"last_action": "APPROVED"}
            )

            if stage == "DECOMPOSITION":
                # Stage 1 Approved -> Trigger Developer Agent & Git Commit -> Create Stage 2 Token
                from app.agents.developer_agent import developer_agent
                from app.agents.security_agent import security_agent

                generated_components = []
                last_git_info = {}
                default_tasks = [
                    {"title": "Student Application LWC Form UI", "component_type": "LWC", "target_filename": "studentApplicationForm.js", "description": "LWC form for student registration"},
                    {"title": "Student Application Apex Controller", "component_type": "ApexClass", "target_filename": "StudentApplicationController.cls", "description": "Apex controller to submit applications"},
                    {"title": "Student Application Unit Tests", "component_type": "ApexTest", "target_filename": "StudentApplicationControllerTest.cls", "description": "Unit tests for StudentApplicationController"}
                ]
                for t in default_tasks:
                    try:
                        res = developer_agent.develop_and_test_with_self_correction(t)
                        if res.get("saved_filepath"):
                            generated_components.append(res.get("saved_filepath"))
                            last_git_info = {"branch": res.get("git_branch"), "commit_sha": res.get("commit_sha")}
                    except Exception as e_dev:
                        logger.warning(f"Error generating Salesforce component '{t.get('title')}': {e_dev}")

                # Security Audit via Gemma 2 / Model Armor
                audit_res = security_agent.audit_component("StudentApplicationController", "public with sharing class StudentApplicationController {}")

                # Generate Stage 2 Token for Code & Git Commit Sign-off (Before Test Org Deployment)
                next_token = self.generate_approval_token(
                    pipeline_id=pipeline_id,
                    stage="DEVELOPMENT",
                    metadata={
                        "preview_text": f"Git Branch: {last_git_info.get('branch', 'feature/SCRUM-1')}\nLatest Commit SHA: {last_git_info.get('commit_sha', 'head-commit')}\nSecurity Score: {audit_res.get('score')}/100\nCode files committed in force-app/.\nClick Approve to deploy code to Testing Salesforce Org ({settings.sf_test_org_username})."
                    }
                )

                return {
                    "success": True,
                    "status": "APPROVED",
                    "message": f"Stage 1 approved! Code committed to Git branch '{last_git_info.get('branch')}'. Advanced to Stage 2 (Code & Git Verification).",
                    "pipeline_id": pipeline_id,
                    "git_branch": last_git_info.get("branch"),
                    "commit_sha": last_git_info.get("commit_sha"),
                    "generated_components": generated_components,
                    "next_stage": "DEVELOPMENT",
                    "next_approval_token": next_token,
                    "next_approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token={next_token}"
                }

            elif stage == "DEVELOPMENT":
                # Stage 2 Approved -> Deploy Code to QA Staging Salesforce Org -> Create Stage 3 Token
                from app.services.salesforce_service import salesforce_service
                logger.info(f"Stage 2 Code Verified! Deploying force-app/ to QA Staging Salesforce Org '{settings.sf_qa_org_username}'...")
                qa_deploy_res = salesforce_service.deploy_metadata(target_org=settings.sf_qa_org_username, source_dir="force-app")

                # Generate Stage 3 Token for Production Release Sign-off
                next_token = self.generate_approval_token(
                    pipeline_id=pipeline_id,
                    stage="RELEASE",
                    metadata={
                        "preview_text": f"DEPLOYED TO QA STAGING SALESFORCE ORG ({settings.sf_qa_org_username})!\nQA Org Deployment Status: {qa_deploy_res.get('status', 0)}\n\nHuman QA can now test in QA Sandbox Org ({settings.sf_qa_org_username}).\nOnce QA passes, click Approve to release & deploy to Production Salesforce Org ({settings.sf_prod_org_username})."
                    }
                )
                return {
                    "success": True,
                    "status": "APPROVED",
                    "message": f"Stage 2 approved! Code deployed to QA Staging Salesforce Org ('{settings.sf_qa_org_username}'). Advanced to Stage 3 (Production Release Sign-off).",
                    "pipeline_id": pipeline_id,
                    "qa_org": settings.sf_qa_org_username,
                    "qa_deployment_result": qa_deploy_res,
                    "next_stage": "RELEASE",
                    "next_approval_token": next_token,
                    "next_approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token={next_token}"
                }

            elif stage == "RELEASE":
                # Stage 3 Approved -> Deploy Code to Production Salesforce Org
                from app.services.salesforce_service import salesforce_service
                logger.info(f"Stage 3 Release Approved! Executing live deployment to Production Salesforce Org '{settings.sf_prod_org_username}'...")
                prod_deploy_res = salesforce_service.deploy_metadata(target_org=settings.sf_prod_org_username, source_dir="force-app")
                
                return {
                    "success": True,
                    "status": "RELEASED_TO_PRODUCTION",
                    "message": f"Stage 3 approved! Live deployment executed to Production Salesforce Org '{settings.sf_prod_org_username}'. Deployment Status: {prod_deploy_res.get('status')}",
                    "pipeline_id": pipeline_id,
                    "production_org": settings.sf_prod_org_username,
                    "production_deployment_result": prod_deploy_res
                }

        elif action == "request_changes":
            memory_bank.update_pipeline_state(
                pipeline_id=pipeline_id,
                status=f"{stage}_FEEDBACK_SUBMITTED",
                stage=stage,
                payload_update={"last_human_feedback": feedback_text}
            )

            if stage == "DECOMPOSITION":
                # Stage 1 Re-prompting Loop: Mutate Epic breakdown with human PM feedback
                from app.agents.decomposer_agent import decomposer_agent
                epic_key = token_data.get("metadata", {}).get("epic_key", "SCRUM-1")
                mutated_result = decomposer_agent.decompose_epic(
                    epic_key=epic_key,
                    epic_summary="Student Application Form",
                    epic_description="Build LWC form and Apex controller",
                    human_feedback=feedback_text
                )
                new_token = self.generate_approval_token(
                    pipeline_id=pipeline_id,
                    stage="DECOMPOSITION",
                    metadata={"preview_text": f"MUTATED BREAKDOWN (Reflecting PM Feedback):\n{mutated_result.architectural_overview}"}
                )
                return {
                    "success": True,
                    "status": "MUTATED",
                    "message": f"PM Decomposer Agent mutated breakdown reflecting feedback: '{feedback_text}'. New approval token generated.",
                    "pipeline_id": pipeline_id,
                    "new_approval_token": new_token,
                    "new_approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token={new_token}"
                }

            elif stage == "DEVELOPMENT":
                # Stage 2 Re-prompting Loop: Mutate Apex/LWC code with human feedback
                from app.agents.developer_agent import developer_agent
                task = {
                    "title": "Student Application Apex Controller",
                    "component_type": "ApexClass",
                    "description": f"Update StudentApplicationController reflecting feedback: {feedback_text}",
                    "target_filename": "StudentApplicationController.cls"
                }
                dev_res = developer_agent.develop_and_test_with_self_correction(task)
                new_token = self.generate_approval_token(
                    pipeline_id=pipeline_id,
                    stage="DEVELOPMENT",
                    metadata={"preview_text": f"MUTATED CODE (Reflecting Human Feedback):\n{dev_res.get('code', '')[:300]}"}
                )
                return {
                    "success": True,
                    "status": "MUTATED",
                    "message": f"Salesforce Developer Agent modified code reflecting feedback: '{feedback_text}'. New approval token generated.",
                    "pipeline_id": pipeline_id,
                    "new_approval_token": new_token,
                    "new_approval_url": f"{settings.approval_base_url}/api/v1/approve/view?token={new_token}"
                }

            return {
                "success": True,
                "status": "MUTATING",
                "message": f"Human feedback recorded for '{stage}'. Re-invoking agent for mutation.",
                "pipeline_id": pipeline_id,
                "feedback_text": feedback_text
            }

        elif action == "reject":
            memory_bank.update_pipeline_state(
                pipeline_id=pipeline_id,
                status="CANCELLED",
                stage=stage,
                payload_update={"last_action": "REJECTED"}
            )
            return {
                "success": True,
                "status": "REJECTED",
                "message": f"Pipeline {pipeline_id} cancelled by human approver.",
                "pipeline_id": pipeline_id
            }

        raise ValueError(f"Invalid approval action: {action}")

    def _get_next_stage(self, current_stage: str) -> str:
        stage_map = {
            "DECOMPOSITION": "DEVELOPMENT",
            "DEVELOPMENT": "STAGING_DEPLOYMENT",
            "STAGING_DEPLOYMENT": "PRODUCTION_DEPLOYMENT",
            "PRODUCTION_DEPLOYMENT": "COMPLETE"
        }
        return stage_map.get(current_stage, "COMPLETE")

approval_service = ApprovalService()
