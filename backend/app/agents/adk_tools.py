import logging
from typing import Dict, Any
from app.services.jira_service import jira_service
from app.services.salesforce_service import salesforce_service
from app.services.git_service import git_service

logger = logging.getLogger("adk_tools")

def get_jira_epic_context(epic_key: str) -> Dict[str, Any]:
    """
    Fetch raw Jira Epic summary and description from Atlassian Cloud.
    
    Args:
        epic_key: Jira Issue Key e.g. SCRUM-1
    """
    logger.info(f"[ADK AFC Tool] Executing get_jira_epic_context for {epic_key}")
    return jira_service.get_issue(epic_key)

def create_jira_story_task(summary: str, description: str, parent_key: str = None) -> Dict[str, Any]:
    """
    Create a new User Story under a Jira Project.
    
    Args:
        summary: Story summary title
        description: Detailed technical description
        parent_key: Parent Epic key e.g. SCRUM-1
    """
    logger.info(f"[ADK AFC Tool] Executing create_jira_story_task: '{summary}'")
    return jira_service.create_story_or_task(parent_key=parent_key, summary=summary, description=description)

def run_salesforce_unit_tests(target_org: str = "dev-org") -> Dict[str, Any]:
    """
    Execute Apex unit tests in target Salesforce Org via SF CLI.
    
    Args:
        target_org: Salesforce username or alias e.g. qa-org or dev-org
    """
    logger.info(f"[ADK AFC Tool] Executing run_salesforce_unit_tests in {target_org}")
    return salesforce_service.run_apex_tests(target_org=target_org)

def save_apex_workspace_file(filename: str, code: str, component_type: str = "ApexClass") -> str:
    """
    Save generated Apex or LWC code to local force-app/ workspace.
    
    Args:
        filename: Target filename e.g. StudentApplicationController.cls
        code: Apex/LWC code content string
        component_type: Type: ApexClass, ApexTest, or LWC
    """
    logger.info(f"[ADK AFC Tool] Executing save_apex_workspace_file: {filename}")
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    force_app = base_dir / "force-app" / "main" / "default"
    
    clean_code = code.replace("```apex", "").replace("```html", "").replace("```javascript", "").replace("```", "").strip()

    if component_type in ["ApexClass", "ApexTest"]:
        classes_dir = force_app / "classes"
        classes_dir.mkdir(parents=True, exist_ok=True)
        cls_file = classes_dir / filename
        cls_file.write_text(clean_code)
        return str(cls_file)
    elif component_type == "LWC":
        lwc_name = filename.replace(".js", "").replace(".html", "")
        lwc_dir = force_app / "lwc" / lwc_name
        lwc_dir.mkdir(parents=True, exist_ok=True)
        js_file = lwc_dir / f"{lwc_name}.js"
        js_file.write_text(clean_code)
        return str(js_file)
    return ""

def execute_git_commit(commit_message: str) -> str:
    """
    Stage force-app/ files and commit changes to current Git feature branch.
    
    Args:
        commit_message: Conventional commit message e.g. feat(student): add controller
    """
    logger.info(f"[ADK AFC Tool] Executing execute_git_commit: '{commit_message}'")
    return git_service.commit_changes(commit_message)

def push_git_feature_branch(branch_name: str = "main") -> bool:
    """
    Push feature branch to remote GitHub origin repository.
    
    Args:
        branch_name: Branch name to push
    """
    logger.info(f"[ADK AFC Tool] Executing push_git_feature_branch for {branch_name}")
    return git_service.push_branch(branch_name)

def deploy_metadata_to_org(target_org: str = "qa-org") -> Dict[str, Any]:
    """
    Deploy force-app/ metadata directory to target Salesforce Org via SF CLI.
    
    Args:
        target_org: Target org username or alias e.g. qa-org or prod-org
    """
    logger.info(f"[ADK AFC Tool] Executing deploy_metadata_to_org for {target_org}")
    return salesforce_service.deploy_metadata(target_org=target_org, source_dir="force-app")
