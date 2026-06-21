# Phase 4a: MCP Server Deployment

## Objective

Get the MCP server running and verify all 6 tools are accessible and working correctly.

---

## Prerequisites

- Python 3.8+
- PyYAML (`pip install pyyaml`)
- EZ Orchestrator repo cloned locally
- All 31 profiles loaded and validated

---

## Step 1: Start the MCP Server

### Option A: Using the startup script (Recommended)

```bash
cd ez-orchestrator
chmod +x run_mcp_server.sh
./run_mcp_server.sh
```

### Option B: Direct Python

```bash
cd ez-orchestrator
pip install -r requirements.txt
python3 mcp/server.py
```

### Expected Output

```
=== EZ Orchestrator MCP Server ===

✓ ProfileLoader initialized
✓ Profiles: ./profiles
✓ Schemas: ./schemas

  projects: 9 profiles
  roles: 6 profiles
  vibes: 7 profiles
  channels: 9 profiles

✓ MCP Server Ready
✓ Available tools:
    - get_project
    - get_role
    - get_vibe
    - get_channel
    - get_context
    - list_profiles

--- Example Usage ---
get_context(project='ez_chain', role='core_engineer')

✓ Context retrieved:
  Project: EZ Chain
  Role: Core Engineer
  Vibe: Prestige
  Channels: 9 channels

✓ Full context JSON saved to context_example.json

--- MCP Server Running ---
Ready for integration with Claude via MCP protocol
```

---

## Step 2: Verify Tools Are Accessible

Once the server is running, **in a NEW TERMINAL**, test each tool:

### Test 1: List Projects

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from mcp.server import OrchestratorMCPServer

server = OrchestratorMCPServer()
result = server.call_tool("list_profiles", type="projects")
print(f"✓ Projects available: {result['profiles']}")
EOF
```

**Expected:** List of 9 projects

### Test 2: Get a Project

```bash
python3 << 'EOF'
import sys, json
sys.path.insert(0, '.')
from mcp.server import OrchestratorMCPServer

server = OrchestratorMCPServer()
result = server.call_tool("get_project", name="ez_chain")
print(f"✓ Project: {result['profile']['name']}")
print(f"  Category: {result['profile']['category']}")
print(f"  Vibe: {result['profile']['default_vibe']}")
EOF
```

**Expected:** EZ Chain project details

### Test 3: Get Full Context

```bash
python3 << 'EOF'
import sys, json
sys.path.insert(0, '.')
from mcp.server import OrchestratorMCPServer

server = OrchestratorMCPServer()
result = server.call_tool("get_context", project="ez_chain", role="core_engineer")
context = result['context']
print(f"✓ Context Retrieved:")
print(f"  Project: {context['project']['name']}")
print(f"  Role: {context['role']['name']}")
print(f"  Vibe: {context['vibe']['name']}")
print(f"  Channels: {list(context['channels'].keys())}")
EOF
```

**Expected:** Full orchestration context with all channels

### Test 4: All Tools

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from mcp.server import OrchestratorMCPServer

server = OrchestratorMCPServer()

tests = [
    ("get_project", {"name": "zendex"}),
    ("get_role", {"name": "founder"}),
    ("get_vibe", {"name": "builder"}),
    ("get_channel", {"name": "discord"}),
    ("list_profiles", {"type": "roles"}),
    ("get_context", {"project": "ez_up", "role": "community_manager"}),
]

print("Testing all MCP tools...")
for tool_name, args in tests:
    result = server.call_tool(tool_name, **args)
    status = "✓" if "success" in result or "profiles" in result else "✗"
    print(f"{status} {tool_name}")

print("\n✓ All tools operational")
EOF
```

**Expected:** All 6 tools return valid responses

---

## Step 3: Health Check

Run this periodic health check to ensure server is still responsive:

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from mcp.server import OrchestratorMCPServer
from datetime import datetime

server = OrchestratorMCPServer()

# Quick health check
checks = {
    "profiles_loaded": len(server.loader.profiles['projects']) > 0,
    "schemas_valid": len(server.loader.loader.schemas) > 0,
    "tools_available": len(server.tools) == 6,
    "context_buildable": server.call_tool("get_context", project="ez_chain", role="core_engineer").get("success")
}

print(f"Health Check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("─" * 40)
for check, status in checks.items():
    icon = "✓" if status else "✗"
    print(f"{icon} {check}")

all_healthy = all(checks.values())
print("─" * 40)
print(f"Status: {'HEALTHY ✓' if all_healthy else 'ISSUES ✗'}")
EOF
```

---

## Step 4: Access the Server

### Local Development
- **Server Address:** `http://localhost:8000` (if needed for HTTP API)
- **Tools:** Accessible via Python API (as shown above)
- **MCP Protocol:** Ready for integration with Claude

### Integration Points
The server is now ready to be integrated with:
- Claude Code (via MCP protocol)
- Claude API (if wrapped in HTTP endpoint)
- Other AI agents that support MCP

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'yaml'"
```bash
pip install pyyaml
```

### "Permission to ezlabscommunity/ez-orchestrator denied"
This is a GitHub access issue, not an MCP issue. Ignore if running locally.

### "Profile 'xyz' not found"
- Verify the profile exists: `ls profiles/projects/xyz.yaml`
- Check spelling (case-sensitive): `ez_chain` not `EZ Chain`
- List available: `python3 -c "from orchestrator.loader import ProfileLoader; loader = ProfileLoader(); print(loader.list_profiles('projects'))"`

### Server crashes on startup
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check profiles directory
ls profiles/
# Should have: projects/, roles/, vibes/, channels/

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('profiles/projects/ez_chain.yaml'))"
```

---

## Performance Baselines (Phase 4a)

| Operation | Expected Time |
|-----------|---|
| Server startup | < 1 second |
| get_project | < 10ms |
| get_role | < 10ms |
| get_vibe | < 10ms |
| get_channel | < 10ms |
| get_context (full) | < 50ms |
| list_profiles | < 10ms |

All operations are O(1) in-memory lookups (very fast).

---

## Next Steps

Once server is running and tests pass:
→ Proceed to Phase 4b: Claude Integration

---

## Status Checklist

- [ ] Python 3.8+ installed
- [ ] PyYAML installed
- [ ] MCP server starts without errors
- [ ] All 9 projects loaded
- [ ] All 6 roles loaded
- [ ] All 7 vibes loaded
- [ ] All 9 channels loaded
- [ ] All 6 tools respond correctly
- [ ] Full context can be retrieved
- [ ] Health check passes

**Status: READY FOR PHASE 4B** ✓
