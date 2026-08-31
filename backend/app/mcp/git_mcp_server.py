import logging
from app.services.git_service import git_service

logger = logging.getLogger("git_mcp_server")

class GitMCPServer:
    """
    GitOps Model Context Protocol (MCP) Server
    Exposes standardized JSON-RPC tool interfaces for feature branching, commit staging, and remote pushes.
    """

    def get_tools(self) -> list:
        return [
            {
                "name": "git_checkout_branch",
                "description": "Create or checkout a Git feature branch",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "branch_name": {"type": "string", "description": "Git branch name e.g. feature/SCRUM-1"}
                    },
                    "required": ["branch_name"]
                }
            },
            {
                "name": "git_commit_staged",
                "description": "Stage force-app/ changes and create a Git commit",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "commit_message": {"type": "string", "description": "Conventional commit message"}
                    },
                    "required": ["commit_message"]
                }
            },
            {
                "name": "git_push_remote",
                "description": "Push feature branch to remote GitHub repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "branch_name": {"type": "string", "description": "Target branch name to push"}
                    },
                    "required": ["branch_name"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "git_checkout_branch":
            branch = git_service.create_or_checkout_branch(arguments.get("branch_name", "main"))
            return {"status": 0, "branch": branch}
        elif tool_name == "git_commit_staged":
            sha = git_service.commit_changes(arguments.get("commit_message", "feat: agent update"))
            return {"status": 0, "commit_sha": sha}
        elif tool_name == "git_push_remote":
            success = git_service.push_branch(arguments.get("branch_name"))
            return {"status": 0 if success else 1, "pushed": success}
        raise ValueError(f"Unknown Git MCP tool: {tool_name}")

git_mcp_server = GitMCPServer()
