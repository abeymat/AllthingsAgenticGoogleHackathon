import sys
import json
import logging
from app.services.jira_service import jira_service

logger = logging.getLogger("jira_mcp_server")

class JiraMCPServer:
    """
    Jira Model Context Protocol (MCP) Server
    Exposes standardized JSON-RPC tool interfaces for Jira Epic & Story operations.
    """

    def get_tools(self) -> list:
        return [
            {
                "name": "jira_get_issue",
                "description": "Fetch details of a Jira Epic or User Story by issue key",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Jira Issue Key e.g. SCRUM-1"}
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "jira_create_story",
                "description": "Create a new User Story under a Jira project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string", "description": "Story summary title"},
                        "description": {"type": "string", "description": "Detailed story description"},
                        "parent_key": {"type": "string", "description": "Optional parent Epic key"}
                    },
                    "required": ["summary", "description"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "jira_get_issue":
            issue_key = arguments.get("issue_key", "SCRUM-1")
            return jira_service.get_issue(issue_key)
        elif tool_name == "jira_create_story":
            return jira_service.create_story_or_task(
                parent_key=arguments.get("parent_key"),
                summary=arguments.get("summary"),
                description=arguments.get("description")
            )
        raise ValueError(f"Unknown Jira MCP tool: {tool_name}")

jira_mcp_server = JiraMCPServer()
