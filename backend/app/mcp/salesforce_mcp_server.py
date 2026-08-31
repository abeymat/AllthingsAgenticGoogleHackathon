import logging
from app.services.salesforce_service import salesforce_service

logger = logging.getLogger("salesforce_mcp_server")

class SalesforceMCPServer:
    """
    Salesforce DX Model Context Protocol (MCP) Server
    Exposes standardized JSON-RPC tool interfaces for SF CLI JWT auth, unit tests, and deployments.
    """

    def get_tools(self) -> list:
        return [
            {
                "name": "sf_authenticate_jwt",
                "description": "Authenticate to a Salesforce org using headless JWT server key",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_user": {"type": "string", "description": "Target Salesforce org username"},
                        "alias": {"type": "string", "description": "Org alias e.g. qa-org"}
                    },
                    "required": ["target_user"]
                }
            },
            {
                "name": "sf_run_apex_tests",
                "description": "Execute Apex unit tests in a target Salesforce org",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_org": {"type": "string", "description": "Target Salesforce org username or alias"}
                    },
                    "required": ["target_org"]
                }
            },
            {
                "name": "sf_deploy_metadata",
                "description": "Deploy force-app/ metadata directory to target Salesforce org",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_org": {"type": "string", "description": "Target Salesforce org username or alias"},
                        "source_dir": {"type": "string", "description": "Directory path e.g. force-app"}
                    },
                    "required": ["target_org"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "sf_authenticate_jwt":
            return salesforce_service.authenticate_jwt(
                username=arguments.get("target_user"),
                alias=arguments.get("alias", "target-org")
            )
        elif tool_name == "sf_run_apex_tests":
            return salesforce_service.run_apex_tests(
                target_org=arguments.get("target_org")
            )
        elif tool_name == "sf_deploy_metadata":
            return salesforce_service.deploy_metadata(
                target_org=arguments.get("target_org"),
                source_dir=arguments.get("source_dir", "force-app")
            )
        raise ValueError(f"Unknown Salesforce MCP tool: {tool_name}")

salesforce_mcp_server = SalesforceMCPServer()
