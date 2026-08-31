import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Jira Configuration
    jira_domain: str = "abeycm.atlassian.net"
    jira_project_key: str = "SCRUM"
    jira_user_email: str = ""
    jira_api_token: str = ""

    # Google Cloud & Gemini Configuration
    gcp_project_id: str = "nexusdev-ai-project"
    gcp_location: str = "us-central1"
    gemini_api_key: str = ""

    # 3-Tier Enterprise Salesforce Orgs (Dev Sandbox -> QA Staging -> Production)
    sf_dev_org_username: str = "abeycm.fbc5eeaa9508@agentforce.com"
    sf_qa_org_username: str = "abeycm@curious-fox-3xbrbu.com"
    sf_prod_org_username: str = "epic.8fb9d0d7217c@orgfarm.salesforce.com"
    
    # Global Shared Credentials (Default for all 3 orgs)
    sf_consumer_key: str = ""
    sf_private_key_path: str = "secrets/server.key"

    # Optional Individual Org Credentials (Fallback to global if omitted)
    sf_dev_consumer_key: str = ""
    sf_qa_consumer_key: str = ""
    sf_prod_consumer_key: str = ""
    sf_dev_private_key_path: str = ""
    sf_qa_private_key_path: str = ""
    sf_prod_private_key_path: str = ""

    # Git Version Control Configuration
    git_repo_url: str = "https://github.com/abeymat/AllthingsAgenticGoogleHackathon.git"
    git_main_branch: str = "main"

    # Approval Engine Configuration
    approval_base_url: str = "http://localhost:8000"
    notification_email_to: str = ""

    # 3 Stage-Specific Human Approval Recipient Emails
    decomposer_approver_email: str = "abeycm@gmail.com"
    developer_approver_email: str = "abeycm@gmail.com"
    release_approver_email: str = "abeycm@gmail.com"

    # Optional SMTP Email Dispatch Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "abeycm@gmail.com"
    smtp_password: str = "afcv xbyn tokh jhhi"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
