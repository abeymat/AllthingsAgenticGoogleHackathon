import logging
from typing import List, Dict, Any
from app.mcp.jira_mcp_server import jira_mcp_server
from app.mcp.salesforce_mcp_server import salesforce_mcp_server
from app.mcp.git_mcp_server import git_mcp_server

logger = logging.getLogger("mcp_client")

class MCPClientGateway:
    """
    Unified Model Context Protocol (MCP) Tool Client Gateway
    Provides tool discovery and JSON-RPC execution bindings across all 5 ADK agents.
    """

    def __init__(self):
        self.servers = {
            "jira": jira_mcp_server,
            "salesforce": salesforce_mcp_server,
            "git": git_mcp_server
        }

    def list_all_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return full list of registered MCP tools across all servers."""
        all_tools = []
        for server_name, server_obj in self.servers.items():
            for tool in server_obj.get_tools():
                tool_copy = dict(tool)
                tool_copy["server"] = server_name
                all_tools.append(tool_copy)
        return all_tools

    def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool invocation to the corresponding MCP server."""
        logger.info(f"MCP Client Gateway dispatching tool call: '{tool_name}' with args: {arguments}")
        
        if tool_name.startswith("jira_"):
            return self.servers["jira"].handle_tool_call(tool_name, arguments)
        elif tool_name.startswith("sf_"):
            return self.servers["salesforce"].handle_tool_call(tool_name, arguments)
        elif tool_name.startswith("git_"):
            return self.servers["git"].handle_tool_call(tool_name, arguments)
        
        raise ValueError(f"No registered MCP server found for tool '{tool_name}'")

mcp_client = MCPClientGateway()
