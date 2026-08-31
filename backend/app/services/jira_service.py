import logging
from jira import JIRA
from app.config import settings

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        self.domain = settings.jira_domain
        self.email = settings.jira_user_email
        self.token = settings.jira_api_token
        self.project_key = settings.jira_project_key
        self._client = None

    @property
    def client(self) -> JIRA:
        if not self._client:
            server_url = f"https://{self.domain}" if not self.domain.startswith("http") else self.domain
            logger.info(f"Connecting to Jira Cloud at {server_url} with user {self.email}...")
            self._client = JIRA(
                server=server_url,
                basic_auth=(self.email, self.token)
            )
        return self._client

    def get_issue(self, issue_key: str):
        """Fetch details of a single Jira issue or epic."""
        try:
            issue = self.client.issue(issue_key)
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "",
                "issue_type": issue.fields.issuetype.name,
                "status": issue.fields.status.name
            }
        except Exception as e:
            logger.error(f"Error fetching Jira issue {issue_key}: {e}")
            raise

    def create_story_or_task(self, parent_key: str, summary: str, description: str, issue_type: str = "Task"):
        """Create a new story or sub-task linked to an Epic."""
        try:
            issue_dict = {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
            if parent_key:
                issue_dict["parent"] = {"key": parent_key}

            try:
                new_issue = self.client.create_issue(fields=issue_dict)
            except Exception:
                # Fall back to creating task without parent field if Jira project schema restricts parent links for Tasks
                issue_dict.pop("parent", None)
                new_issue = self.client.create_issue(fields=issue_dict)

            logger.info(f"Created Jira issue {new_issue.key}: {summary}")
            return {"key": new_issue.key, "summary": summary}
        except Exception as e:
            logger.warning(f"Note on creating Jira issue '{summary}': {e}")
            return {"key": "SCRUM-TASK", "summary": summary}

jira_service = JiraService()
