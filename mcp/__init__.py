"""
EZ Orchestrator MCP Server

Exposes the ProfileLoader as an MCP (Model Context Protocol) server
for integration with Claude and other AI agents.
"""

from mcp.server import OrchestratorMCPServer

__version__ = "0.1.0"
__all__ = ["OrchestratorMCPServer"]
