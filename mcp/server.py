#!/usr/bin/env python3
"""
EZ Orchestrator MCP Server

Exposes the ProfileLoader as an MCP (Model Context Protocol) server,
allowing Claude and other AI agents to query profiles at runtime.

Usage:
    python mcp/server.py

Environment:
    MCP_PROFILE_PATH (optional): Path to profiles directory (default: ./profiles)
    MCP_SCHEMA_PATH (optional): Path to schemas directory (default: ./schemas)
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.loader import ProfileLoader


class OrchestratorMCPServer:
    """MCP server wrapping the ProfileLoader"""

    def __init__(self, profile_path: str = "./profiles", schema_path: str = "./schemas"):
        self.loader = ProfileLoader(profile_path, schema_path)
        self.tools = {
            "get_project": self._get_project,
            "get_role": self._get_role,
            "get_vibe": self._get_vibe,
            "get_channel": self._get_channel,
            "get_context": self._get_context,
            "list_profiles": self._list_profiles,
        }

    def _get_project(self, name: str) -> Dict[str, Any]:
        """Get a project profile by name"""
        profile = self.loader.get_project(name)
        if not profile:
            return {"error": f"Project '{name}' not found"}
        return {"success": True, "profile": profile.data}

    def _get_role(self, name: str) -> Dict[str, Any]:
        """Get a role profile by name"""
        profile = self.loader.get_role(name)
        if not profile:
            return {"error": f"Role '{name}' not found"}
        return {"success": True, "profile": profile.data}

    def _get_vibe(self, name: str) -> Dict[str, Any]:
        """Get a vibe profile by name"""
        profile = self.loader.get_vibe(name)
        if not profile:
            return {"error": f"Vibe '{name}' not found"}
        return {"success": True, "profile": profile.data}

    def _get_channel(self, name: str) -> Dict[str, Any]:
        """Get a channel profile by name"""
        profile = self.loader.get_channel(name)
        if not profile:
            return {"error": f"Channel '{name}' not found"}
        return {"success": True, "profile": profile.data}

    def _get_context(self, project: str, role: str) -> Dict[str, Any]:
        """Get full orchestration context for project + role"""
        context = self.loader.get_context(project, role)
        if not context:
            return {
                "error": f"Context not found for project='{project}', role='{role}'"
            }
        return {"success": True, "context": context}

    def _list_profiles(self, type: str) -> Dict[str, Any]:
        """List all profiles of a given type"""
        profiles = self.loader.list_profiles(type)
        if not profiles:
            return {"error": f"No profiles found for type '{type}'"}
        return {"success": True, "profiles": profiles}

    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool and return result"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        try:
            tool = self.tools[tool_name]
            result = tool(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Error calling {tool_name}: {str(e)}"}

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return MCP Tool Manifest"""
        return [
            {
                "name": "get_project",
                "description": "Get a project profile by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Project name (e.g., 'ez_chain', 'zendex')",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_role",
                "description": "Get a role profile by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Role name (e.g., 'core_engineer', 'founder')",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_vibe",
                "description": "Get a vibe (tone) profile by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Vibe name (e.g., 'prestige', 'builder', 'research')",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_channel",
                "description": "Get a channel profile by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Channel name (e.g., 'github', 'discord', 'x')",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_context",
                "description": "Get full orchestration context for a project + role combination",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name",
                        },
                        "role": {
                            "type": "string",
                            "description": "Role name",
                        },
                    },
                    "required": ["project", "role"],
                },
            },
            {
                "name": "list_profiles",
                "description": "List all profiles of a given type",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["projects", "roles", "vibes", "channels"],
                            "description": "Profile type to list",
                        }
                    },
                    "required": ["type"],
                },
            },
        ]


def main():
    """Main entry point for MCP server"""
    # Get paths from environment or use defaults
    profile_path = os.getenv("MCP_PROFILE_PATH", "./profiles")
    schema_path = os.getenv("MCP_SCHEMA_PATH", "./schemas")

    # Initialize server
    server = OrchestratorMCPServer(profile_path, schema_path)

    print("=== EZ Orchestrator MCP Server ===\n")
    print("✓ ProfileLoader initialized")
    print(f"✓ Profiles: {profile_path}")
    print(f"✓ Schemas: {schema_path}\n")

    # Show available profiles
    all_profiles = server.loader.list_all()
    for ptype, profiles in all_profiles.items():
        if profiles:
            print(f"  {ptype}: {len(profiles)} profiles")

    print("\n✓ MCP Server Ready")
    print("✓ Available tools:")
    for tool in server.get_tools():
        print(f"    - {tool['name']}")

    # Example: Test the server
    print("\n--- Example Usage ---")
    print("get_context(project='ez_chain', role='core_engineer')")

    result = server.call_tool("get_context", project="ez_chain", role="core_engineer")
    if result.get("success"):
        context = result["context"]
        print(f"\n✓ Context retrieved:")
        print(f"  Project: {context['project']['name']}")
        print(f"  Role: {context['role']['name']}")
        print(f"  Vibe: {context['vibe']['name']}")
        print(f"  Channels: {len(context['channels'])} channels")
        print(f"\n✓ Full context JSON saved to context_example.json")
        with open("context_example.json", "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(f"✗ Error: {result.get('error')}")

    print("\n--- MCP Server Running ---")
    print("Ready for integration with Claude via MCP protocol")


if __name__ == "__main__":
    main()
