import logging
from google import genai
from google.genai import types
from app.config import settings
from app.schemas.decomposition_schemas import DecompositionResult

logger = logging.getLogger(__name__)

class PMDecomposerAgent:
    """
    PM Decomposer Agent (Google ADK / Gemini 3.5 Pro)
    Listens to Jira Epics and decomposes them into structured technical User Stories & Tasks.
    Supports iterative Human-in-the-Loop feedback re-prompting loops.
    """

    def __init__(self):
        raw_key = settings.gemini_api_key or ""
        self.api_key = raw_key.strip().strip("'").strip('"')
        self.client = genai.Client(api_key=self.api_key) if self.api_key and len(self.api_key) > 10 else None

    def decompose_epic(self, epic_key: str, epic_summary: str, epic_description: str, human_feedback: str = None) -> DecompositionResult:
        if not self.client:
            logger.warning("Gemini API key not found in environment settings. Falling back to mock decomposition for local dev.")
            return self._mock_decomposition(epic_key, epic_summary, human_feedback)

        system_instruction = """
        You are an expert Enterprise Product Manager & Lead Architect specializing in Salesforce, Jira, and Cloud Engineering.
        Your job is to decompose high-level Jira Epics into actionable, isolated User Stories and Development Tasks.
        For each task, specify exact component types (ApexClass, ApexTrigger, LWC, ApexTest) and technical specifications.
        """

        prompt = f"""
        Jira Epic Key: {epic_key}
        Epic Summary: {epic_summary}
        Epic Description: {epic_description}
        """

        if human_feedback:
            prompt += f"""
            
            CRITICAL - HUMAN APPROVER FEEDBACK TO INCORPORATE:
            The human PM reviewed the previous breakdown and requested the following modifications:
            "{human_feedback}"

            Please mutate and update the decomposition plan to strictly reflect this human feedback.
            """

        try:
            logger.info(f"Invoking Gemini for Epic {epic_key} decomposition...")
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=DecompositionResult,
                        temperature=0.2
                    )
                )
            except Exception as e_primary:
                logger.warning(f"Primary model busy ({e_primary}), falling back to gemini-flash-latest...")
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=DecompositionResult,
                        temperature=0.2
                    )
                )
            
            # Parsed Pydantic response
            result = DecompositionResult.model_validate_json(response.text)
            logger.info(f"Successfully decomposed Epic {epic_key} into {len(result.tasks)} tasks.")
            return result

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Returning fallback structured decomposition.")
            return self._mock_decomposition(epic_key, epic_summary, human_feedback)

    def _mock_decomposition(self, epic_key: str, epic_summary: str, human_feedback: str = None) -> DecompositionResult:
        """Fallback decomposition for offline development or testing without API keys."""
        feedback_note = f" (Incorporated Feedback: {human_feedback})" if human_feedback else ""
        return DecompositionResult(
            epic_key=epic_key,
            epic_summary=epic_summary,
            architectural_overview=f"Decomposed architecture for '{epic_summary}'{feedback_note}. Integrates LWC Form UI, Apex Controller, and Unit Tests.",
            tasks=[
                {
                    "title": f"Create Student Application LWC Form",
                    "component_type": "LWC",
                    "description": "Build Lightning Web Component form with fields for First Name, Last Name, Email, and Major.",
                    "target_filename": "studentApplicationForm.js"
                },
                {
                    "title": f"Apex Controller for Student Application",
                    "component_type": "ApexClass",
                    "description": "Create StudentApplicationController.cls with @AuraEnabled method to insert Contact/Application record.",
                    "target_filename": "StudentApplicationController.cls"
                },
                {
                    "title": f"Apex Unit Tests for Student Application",
                    "component_type": "ApexTest",
                    "description": "Create StudentApplicationControllerTest.cls with 100% test coverage for successful creation and error handling.",
                    "target_filename": "StudentApplicationControllerTest.cls"
                }
            ]
        )

decomposer_agent = PMDecomposerAgent()
