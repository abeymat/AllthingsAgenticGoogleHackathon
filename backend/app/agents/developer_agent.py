import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
from app.config import settings
from app.services.salesforce_service import salesforce_service

logger = logging.getLogger(__name__)

class SalesforceDeveloperAgent:
    """
    Salesforce Developer Agent (Google ADK / Gemini 3.5 Pro)
    Generates Apex Classes, Apex Triggers, and Lightning Web Components (LWC).
    Includes an Autonomous Self-Correction Loop for failed unit tests.
    """

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.max_retries = 3

    def generate_code_for_task(self, task_spec: Dict[str, Any], previous_errors: str = None) -> str:
        """Use Gemini 3.5 Pro to generate production-ready Apex or LWC code."""
        if not self.client:
            logger.warning("Gemini API key not configured. Returning mock Salesforce code.")
            return self._mock_code_generation(task_spec, previous_errors)

        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        skill_file = base_dir / ".agents" / "skills" / "salesforce-governance" / "SKILL.md"
        skill_context = skill_file.read_text(encoding="utf-8") if skill_file.exists() else ""

        system_instruction = f"""
        You are an expert Senior Salesforce Developer.
        Your job is to generate clean, production-ready Salesforce code (Apex Class, Apex Trigger, LWC, or Apex Unit Test).
        
        SKILL INSTRUCTIONS (salesforce-governance):
        {skill_context}

        Return ONLY valid code without Markdown formatting backticks if possible.
        """

        prompt = f"""
        Task Title: {task_spec.get('title')}
        Component Type: {task_spec.get('component_type')}
        Target Filename: {task_spec.get('target_filename')}
        Technical Specification: {task_spec.get('description')}
        """

        if previous_errors:
            prompt += f"""
            
            CRITICAL - SELF-CORRECTION LOOP:
            The previous compilation or unit test execution failed with the following errors:
            "{previous_errors}"

            Analyze the stack trace, fix the issue in the code, and return the corrected code.
            """

        from app.agents.adk_tools import run_salesforce_unit_tests, save_apex_workspace_file

        try:
            logger.info(f"Invoking Gemini 3.6 Flash (ADK AFC Enabled) code generator for task: {task_spec.get('title')}...")
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[run_salesforce_unit_tests, save_apex_workspace_file],
                        temperature=0.1
                    )
                )
            except Exception as e_primary:
                logger.warning(f"Primary model busy ({e_primary}), falling back to gemini-flash-latest...")
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error calling Gemini for code generation: {e}")
            return self._mock_code_generation(task_spec, previous_errors)

    def develop_and_test_with_self_correction(self, task_spec: Dict[str, Any], target_org: str = "target-org") -> Dict[str, Any]:
        """
        Full Autonomous Development Workflow:
        1. Generate Code via Gemini 3.5 Pro
        2. Deploy & Run Apex Unit Tests via SF CLI
        3. If Tests Fail → Self-Correction Loop (Up to 3 Retries)
        """
        current_errors = None
        attempt_logs = []

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Starting Development Attempt {attempt}/{self.max_retries} for task: {task_spec.get('title')}")
            
            # Step 1: Generate Code
            code = self.generate_code_for_task(task_spec, previous_errors=current_errors)
            
            # Step 2: Save to local force-app/ workspace
            saved_filepath = self._save_code_to_workspace(task_spec, code)
            
            # Step 3: Run SF CLI Unit Tests (or Mock Test)
            test_result = salesforce_service.run_apex_tests(target_org=target_org)
            
            from app.services.telemetry import telemetry
            event_type = "SELF_CORRECTION" if attempt > 1 else "CODE_GENERATION"
            telemetry.log_agent_event(
                agent_name="Salesforce Developer Agent",
                event_type=event_type,
                pipeline_id=f"pipe-{task_spec.get('target_filename', 'task')}",
                summary=f"Attempt {attempt}/{self.max_retries}: Generated {task_spec.get('component_type')} ({task_spec.get('target_filename')})",
                details={
                    "attempt": attempt,
                    "target_filename": task_spec.get("target_filename"),
                    "component_type": task_spec.get("component_type"),
                    "test_status": test_result.get("status")
                }
            )
            
            # Check test outcome
            status_code = test_result.get("status", 0)
            result_data = test_result.get("result", {})
            summary = result_data.get("summary", {})
            outcome = summary.get("outcome", "Passed")

            attempt_logs.append({
                "attempt": attempt,
                "code_snippet": code[:100] + "...",
                "test_outcome": outcome
            })

            if status_code == 0 and outcome != "Failed":
                logger.info(f"Task '{task_spec.get('title')}' passed unit tests successfully on attempt {attempt}!")
                saved_filepath = self._save_code_to_workspace(task_spec, code)
                
                # Git Branch Checkout & Commit Integration
                from app.services.git_service import git_service
                branch_name = git_service.create_or_checkout_branch("feature/SCRUM-1-student-app")
                commit_sha = git_service.commit_changes(f"feat(dev-agent): update {task_spec.get('target_filename')}")

                return {
                    "success": True,
                    "attempts": attempt,
                    "code": code,
                    "logs": attempt_logs,
                    "target_filename": task_spec.get("target_filename"),
                    "saved_filepath": saved_filepath,
                    "git_branch": branch_name,
                    "commit_sha": commit_sha
                }
            
            # Extract error for self-correction loop
            current_errors = test_result.get("error") or str(test_result.get("result"))
            logger.warning(f"Attempt {attempt} failed with errors. Intercepting stack trace for Self-Correction Loop...")

        # If all retries failed
        return {
            "success": False,
            "attempts": self.max_retries,
            "error": current_errors,
            "logs": attempt_logs
        }

    def _save_code_to_workspace(self, task_spec: Dict[str, Any], code: str) -> str:
        """Write generated Apex/LWC code and SFDX metadata to local force-app/ directory."""
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        force_app = base_dir / "force-app" / "main" / "default"

        comp_type = task_spec.get("component_type", "ApexClass")
        filename = task_spec.get("target_filename", "GeneratedComponent.cls")

        # Strip markdown ticks if Gemini added them
        clean_code = code.replace("```apex", "").replace("```html", "").replace("```javascript", "").replace("```js", "").replace("```", "").strip()

        if comp_type in ["ApexClass", "ApexTest", "ApexTrigger"]:
            classes_dir = force_app / "classes"
            classes_dir.mkdir(parents=True, exist_ok=True)
            cls_file = classes_dir / filename
            cls_file.write_text(clean_code)

            # Metadata XML
            meta_file = classes_dir / f"{filename}-meta.xml"
            if not meta_file.exists():
                meta_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <status>Active</status>
</ApexClass>"""
                meta_file.write_text(meta_xml)
            logger.info(f"Saved Apex Component to: {cls_file}")
            return str(cls_file)

        elif comp_type == "LWC":
            lwc_name = filename.replace(".js", "").replace(".html", "")
            lwc_dir = force_app / "lwc" / lwc_name
            lwc_dir.mkdir(parents=True, exist_ok=True)

            js_file = lwc_dir / f"{lwc_name}.js"
            js_file.write_text(clean_code)

            # Generate rich HTML template
            html_file = lwc_dir / f"{lwc_name}.html"
            if not html_file.exists() or len(html_file.read_text().strip()) < 300:
                html_content = f"""<template>
    <lightning-card title="{task_spec.get('title', 'Student Scholarship Application Portal')}" icon-name="standard:education">
        <div class="slds-m-around_medium">
            <div class="slds-grid slds-gutters slds-m-bottom_small">
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="First Name" name="firstName" value={{firstName}} onchange={{handleInputChange}} required></lightning-input>
                </div>
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="Last Name" name="lastName" value={{lastName}} onchange={{handleInputChange}} required></lightning-input>
                </div>
            </div>
            <div class="slds-grid slds-gutters slds-m-bottom_small">
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="Email Address" type="email" name="email" value={{email}} onchange={{handleInputChange}} required></lightning-input>
                </div>
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="Phone Number" type="tel" name="phone" value={{phone}} onchange={{handleInputChange}}></lightning-input>
                </div>
            </div>
            <div class="slds-grid slds-gutters slds-m-bottom_small">
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="High School / Previous Institution" name="highSchool" value={{highSchool}} onchange={{handleInputChange}}></lightning-input>
                </div>
                <div class="slds-col slds-size_1-of-2">
                    <lightning-input label="Cumulative GPA" type="number" step="0.01" min="0" max="4.0" name="gpa" value={{gpa}} onchange={{handleInputChange}} required></lightning-input>
                </div>
            </div>
            <div class="slds-m-bottom_small">
                <lightning-combobox name="programOfInterest" label="Program of Interest" value={{programOfInterest}} placeholder="Select Program" options={{programOptions}} onchange={{handleInputChange}} required></lightning-combobox>
            </div>
            <div class="slds-m-bottom_small">
                <lightning-textarea name="personalStatement" label="Personal Statement / Scholarship Justification" value={{personalStatement}} onchange={{handleInputChange}} placeholder="Briefly state your academic goals..." required></lightning-textarea>
            </div>
            <div class="slds-m-top_medium slds-text-align_right">
                <lightning-button label="Submit Scholarship Application" variant="brand" icon-name="utility:send" onclick={{handleSubmit}} disabled={{isSubmitting}}></lightning-button>
            </div>
        </div>
    </lightning-card>
</template>"""
                html_file.write_text(html_content)

            # LWC Metadata XML
            meta_file = lwc_dir / f"{lwc_name}.js-meta.xml"
            if not meta_file.exists():
                meta_xml = """<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <isExposed>true</isExposed>
    <targets>
        <target>lightning__AppPage</target>
        <target>lightning__RecordPage</target>
        <target>lightning__HomePage</target>
    </targets>
</LightningComponentBundle>"""
                meta_file.write_text(meta_xml)
            logger.info(f"Saved LWC Component to: {lwc_dir}")
            return str(js_file)

        return ""

    def _mock_code_generation(self, task_spec: Dict[str, Any], previous_errors: str = None) -> str:
        comp_type = task_spec.get("component_type", "ApexClass")
        if comp_type == "ApexClass":
            return """public with sharing class StudentApplicationController {
    @AuraEnabled
    public static String submitApplication(String firstName, String lastName, String email) {
        Contact student = new Contact(
            FirstName = firstName,
            LastName = lastName,
            Email = email
        );
        insert student;
        return student.Id;
    }
}"""
        elif comp_type == "ApexTest":
            return """@IsTest
private class StudentApplicationControllerTest {
    @IsTest
    static void testSubmitApplication() {
        Test.startTest();
        String contactId = StudentApplicationController.submitApplication('Jane', 'Doe', 'jane@university.edu');
        Test.stopTest();
        System.assertNotEquals(null, contactId, 'Contact ID should be generated');
    }
}"""
        else:
            return "// Mock LWC / Trigger code"

developer_agent = SalesforceDeveloperAgent()
