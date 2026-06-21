# EZ Orchestrator MCP Integration Guide

## Overview

The EZ Orchestrator MCP Server exposes the ProfileLoader as tools via the Model Context Protocol (MCP), allowing Claude and other AI agents to query profiles dynamically at runtime.

---

## Architecture

```
Claude / AI Agent
    ↓
MCP Protocol
    ↓
OrchestratorMCPServer
    ↓
ProfileLoader
    ↓
Profile Graph (YAML)
```

---

## Available Tools

### 1. `get_project`

**Purpose:** Retrieve a project profile

**Input:**
```json
{
  "name": "ez_chain"
}
```

**Output:**
```json
{
  "success": true,
  "profile": {
    "name": "EZ Chain",
    "description": "Proof-of-Active-Human blockchain infrastructure...",
    "category": "infrastructure",
    "pillars": [...],
    "default_vibe": "prestige",
    ...
  }
}
```

### 2. `get_role`

**Purpose:** Retrieve a role profile

**Input:**
```json
{
  "name": "core_engineer"
}
```

**Output:**
```json
{
  "success": true,
  "profile": {
    "name": "Core Engineer",
    "description": "Senior technical leader...",
    "authority_level": "strategic",
    "responsibilities": [...],
    ...
  }
}
```

### 3. `get_vibe`

**Purpose:** Retrieve a vibe (tone) profile

**Input:**
```json
{
  "name": "prestige"
}
```

**Output:**
```json
{
  "success": true,
  "profile": {
    "name": "Prestige",
    "description": "Professional, authoritative tone...",
    "tone_characteristics": {...},
    "language_guidelines": [...],
    ...
  }
}
```

### 4. `get_channel`

**Purpose:** Retrieve a channel profile

**Input:**
```json
{
  "name": "github"
}
```

**Output:**
```json
{
  "success": true,
  "profile": {
    "name": "GitHub",
    "description": "Code review, technical discussion...",
    "constraints": {...},
    "best_practices": [...],
    ...
  }
}
```

### 5. `get_context`

**Purpose:** Get full orchestration context for project + role

**Input:**
```json
{
  "project": "ez_chain",
  "role": "core_engineer"
}
```

**Output:**
```json
{
  "success": true,
  "context": {
    "project": {...},
    "role": {...},
    "vibe": {...},
    "secondary_vibes": [...],
    "channels": {
      "github": {...},
      "discord": {...},
      ...
    }
  }
}
```

### 6. `list_profiles`

**Purpose:** List all profiles of a given type

**Input:**
```json
{
  "type": "projects"
}
```

**Output:**
```json
{
  "success": true,
  "profiles": [
    "ez_chain",
    "zendex",
    "ez_path",
    "ez_up",
    "ezverse",
    "ojet3d",
    "ez_secure",
    "crypto_news_org",
    "tech_news_studio"
  ]
}
```

---

## Integration with Claude

### Using the MCP Server in Claude Code

The orchestrator MCP server is designed to work seamlessly with Claude Code and Claude API:

#### 1. Start the MCP Server

```bash
cd ez-orchestrator
python mcp/server.py
```

This starts the server and prints available tools:
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
```

#### 2. Use in Prompts

Once the MCP server is running, Claude can use these tools directly:

```
You are the EZ Labs content orchestrator.

Use the orchestrator tools to:
1. Get the current project context: get_project("ez_chain")
2. Get the writing role: get_role("core_engineer")
3. Get the tone/vibe: get_vibe("prestige")
4. Get the target channel: get_channel("github")

Then shape your output based on the profiles.
```

#### 3. Example: Context-Aware Output

```
[Claude queries]: get_context(project="ez_chain", role="core_engineer")

[Claude receives]:
{
  "project": {name: "EZ Chain", vibe: "prestige", ...},
  "role": {authority_level: "strategic", ...},
  "vibe": {formality: "high", language_guidelines: [...], ...},
  "channels": {
    "github": {formatting_rules: {...}, best_practices: [...], ...},
    "discord": {...},
    ...
  }
}

[Claude generates output]:
"For a GitHub PR (technical channel) + prestige vibe + strategic role,
I should write: [Markdown format] + [professional language] + 
[data-driven arguments] + [verified facts] + [clear tradeoffs]"
```

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- PyYAML

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify profiles are loaded:**
```bash
python mcp/server.py
```

### Configuration

**Environment variables:**
- `MCP_PROFILE_PATH` (default: `./profiles`) — Path to profiles directory
- `MCP_SCHEMA_PATH` (default: `./schemas`) — Path to schemas directory

**Example:**
```bash
export MCP_PROFILE_PATH=/path/to/profiles
export MCP_SCHEMA_PATH=/path/to/schemas
python mcp/server.py
```

---

## Real-World Examples

### Example 1: Write a GitHub PR

```
Context:
  - Project: EZ Chain (infrastructure)
  - Role: Core Engineer (strategic)
  - Channel: GitHub (technical)
  - Vibe: Prestige (professional, data-driven)

Query: get_context("ez_chain", "core_engineer")

Claude generates:
"""
# refactor: simplify consensus validation logic

## Why
The current validation loop has a race condition causing 30-50% request 
failures under concurrency (fixes #456).

## What Changed
- Refactored token validation to use RwLock instead of Mutex
- Moved token parsing outside the critical section
- Added dedicated benchmark for concurrent validation

## Testing
- Unit tests: 24/24 passing
- Concurrent stress test: 100% success rate
- Benchmark: 40% improvement in concurrent throughput
"""
```

### Example 2: Write a Discord Announcement

```
Context:
  - Project: EZ UP (creative)
  - Role: Community Manager (operational)
  - Channel: Discord (real-time)
  - Vibe: Builder (pragmatic, shipping-focused)

Query: get_context("ez_up", "community_manager")

Claude generates:
"""
🚀 **EZ UP launched today!**

Drop your creative content. Get rewards. Watch your audience grow.

[Get started →] [Read docs] [Join Discord]
"""
```

### Example 3: Write a Newsletter

```
Context:
  - Project: Tech News Studio (content)
  - Role: Founder (executive)
  - Channel: Beehiiv (email)
  - Vibe: Prestige (authoritative)

Query: get_context("tech_news_studio", "founder")

Claude generates:
"""
Subject: This week in web3 infrastructure

The convergence of zero-knowledge proofs, deterministic routing, and 
human-verified consensus is reshaping blockchain architecture.

Here's what happened this week and why it matters...

[Read full analysis →]
"""
```

---

## Integration Patterns

### Pattern 1: Route by Channel

```python
# Claude gets the channel, applies its formatting rules
channel = get_channel("x")
# Output: 280 chars max, hashtags, urgency, visual hook
```

### Pattern 2: Apply Vibe

```python
# Claude gets the vibe, applies tone guidelines
vibe = get_vibe("prestige")
# Output: Professional, authoritative, data-driven, formal language
```

### Pattern 3: Full Context

```python
# Claude gets everything at once
context = get_context("zendex", "ai_builder")
# Output shaped by: project + role + vibe + all channels
```

### Pattern 4: List and Choose

```python
# Claude lists available projects
projects = list_profiles("projects")
# Then chooses one and gets its context
```

---

## Error Handling

All tools return a standard response:

**Success:**
```json
{
  "success": true,
  "profile": {...} or "context": {...} or "profiles": [...]
}
```

**Error:**
```json
{
  "error": "Profile 'nonexistent' not found"
}
```

Claude should handle errors gracefully:
- If a profile isn't found, ask the user which project/role/channel they meant
- If context is incomplete, use the individual tools
- Provide helpful error messages referencing valid options

---

## Performance Considerations

### Caching
- Profiles are loaded once on server startup
- Subsequent queries are O(1) dictionary lookups
- No network latency (local file system)

### Optimization
- Get `get_context()` for full info (one query)
- Use individual tools only if you need partial info
- List tools for discovery

---

## Extending the MCP Server

### Adding New Tools

1. Add a method to `OrchestratorMCPServer`:
```python
def _my_new_tool(self, param: str) -> Dict[str, Any]:
    # Implementation
    return {"success": True, "data": result}
```

2. Register in `__init__`:
```python
self.tools = {
    ...
    "my_new_tool": self._my_new_tool,
}
```

3. Add to `get_tools()` with schema

### Extending Profiles

Add new profiles to `profiles/{type}/` and they're automatically available to the MCP server.

---

## Testing

### Test the MCP Server

```bash
# Start server
python mcp/server.py

# In another terminal, test a tool
python -c "
from mcp.server import OrchestratorMCPServer
server = OrchestratorMCPServer()
result = server.call_tool('get_context', project='ez_chain', role='core_engineer')
print(result)
"
```

### Test with Claude

Use Claude Code with this prompt:

```
Use the orchestrator tools to:
1. Get all available projects
2. Get the core_engineer role
3. Build the context for ez_chain + core_engineer
4. Show me the prestige vibe
```

---

## Troubleshooting

### "Profile not found"
- Check spelling: profile names use snake_case
- List available profiles: `list_profiles("projects")`
- Verify file exists: `ls profiles/{type}/`

### "Server not starting"
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check paths: `echo $MCP_PROFILE_PATH`

### "Profiles not loading"
- Verify YAML syntax: `python orchestrator/loader.py`
- Check file permissions: `ls -la profiles/`
- Validate against schema: profiles should follow schema constraints

---

## Next Steps

1. **Deploy MCP Server** — Run in production environment
2. **Integrate with Claude** — Add MCP tools to Claude Code settings
3. **Build Orchestrator Engine** — Use profiles to shape Claude outputs
4. **Monitor Usage** — Track which profiles/tools are most used
5. **Iterate Profiles** — Refine based on real-world usage

---

## API Reference

### OrchestratorMCPServer

```python
class OrchestratorMCPServer:
    def __init__(self, profile_path: str = "./profiles", schema_path: str = "./schemas")
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]
    def get_tools(self) -> List[Dict[str, Any]]
    
    # Individual tools
    def _get_project(self, name: str) -> Dict[str, Any]
    def _get_role(self, name: str) -> Dict[str, Any]
    def _get_vibe(self, name: str) -> Dict[str, Any]
    def _get_channel(self, name: str) -> Dict[str, Any]
    def _get_context(self, project: str, role: str) -> Dict[str, Any]
    def _list_profiles(self, type: str) -> Dict[str, Any]
```

---

**MCP Integration Status: Ready for Claude Integration** ✓
