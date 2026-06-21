# Phase 4b: Claude MCP Integration

## Objective

Integrate the EZ Orchestrator MCP server with Claude so Claude can dynamically load and apply orchestrator profiles to generate context-aware outputs.

---

## The Goal

After Phase 4b, Claude will:

✓ Query orchestrator profiles at runtime  
✓ Load project/role/vibe/channel contexts  
✓ Shape outputs based on profiles  
✓ Generate deterministic, verifiable outputs  
✓ Be profile-aware, vibe-aware, channel-aware  

---

## Architecture

```
Claude (with MCP tools loaded)
    ↓
Calls MCP tools:
  - get_context("ez_chain", "core_engineer")
  - get_vibe("prestige")
  - get_channel("github")
    ↓
MCP Server
    ↓
ProfileLoader
    ↓
Returns profiles + formatting rules
    ↓
Claude applies to generation
    ↓
Output shaped by: project + role + vibe + channel
```

---

## Setup Steps

### Step 1: Ensure MCP Server Is Running

```bash
# Terminal 1: Start the server
cd ez-orchestrator
python3 mcp/server.py

# Expected output:
# ✓ MCP Server Ready
# ✓ Available tools:
#     - get_project
#     - get_role
#     - get_vibe
#     - get_channel
#     - get_context
#     - list_profiles
```

### Step 2: Configure Claude Code Settings

**If using Claude Code CLI:**

Create `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python3",
      "args": [
        "/path/to/ez-orchestrator/mcp/server.py"
      ],
      "env": {
        "MCP_PROFILE_PATH": "/path/to/ez-orchestrator/profiles",
        "MCP_SCHEMA_PATH": "/path/to/ez-orchestrator/schemas"
      }
    }
  }
}
```

Replace `/path/to/ez-orchestrator` with actual path.

### Step 3: Test MCP Connection

In Claude, verify the tools are available:

```
I have access to these MCP tools. Can you list them?
```

Expected response:
```
I have access to the following MCP tools:
- get_project
- get_role
- get_vibe
- get_channel
- get_context
- list_profiles
```

---

## Usage Patterns

### Pattern 1: Load Full Context

**Claude Query:**
```
Get the full orchestration context for EZ Chain + Core Engineer
```

**Claude Action:**
```
Calling: get_context(project="ez_chain", role="core_engineer")
```

**Claude Receives:**
```json
{
  "project": {
    "name": "EZ Chain",
    "category": "infrastructure",
    "default_vibe": "prestige",
    "channels": ["github", "discord", "x", ...],
    ...
  },
  "role": {
    "name": "Core Engineer",
    "authority_level": "strategic",
    "vibe_affinity": ["prestige", "builder", "research"],
    ...
  },
  "vibe": {
    "name": "Prestige",
    "tone_characteristics": {...},
    "do_list": [...],
    ...
  },
  "channels": {
    "github": {...},
    "discord": {...},
    ...
  }
}
```

### Pattern 2: Shape Output by Context

**Claude System Prompt:**
```
You are the EZ Labs orchestrator. When generating outputs:

1. Call get_context(project, role) to load orchestration context
2. Extract the vibe profile
3. Extract the channel profile  
4. Apply formatting rules from the channel
5. Apply tone from the vibe
6. Follow best practices from the profile
7. Generate output shaped by all three

Example:
- Project: ez_chain
- Role: core_engineer
- Channel: github
→ Generate: Markdown PR with professional tone, data-driven language, linked issues
```

### Pattern 3: Multi-Profile Merging

**Claude Query:**
```
Write a Discord announcement for EZ UP's creator rewards launch.
Project: ez_up, Role: community_manager
```

**Claude Process:**
1. `get_context("ez_up", "community_manager")`
2. Extract vibe: "builder" (pragmatic, shipping-focused)
3. Extract channel: "discord" (real-time, threads, emoji)
4. Merge: builder tone + discord format = informal, energetic announcement
5. Generate output

---

## Testing Checklist

### Test 1: Tool Availability
```
Can you list what MCP tools you have available?
```
✓ Should show 6 tools

### Test 2: Get Project
```
Use get_project to retrieve the ZENDEX profile
```
✓ Should return ZENDEX details (trading platform, prestige vibe)

### Test 3: Get Full Context
```
Get the full context for EZ Path + AI Builder
```
✓ Should return: ez_path profile + ai_builder profile + builder vibe + all channels

### Test 4: Context Application
```
Based on the EZ Chain + Core Engineer context, write a GitHub PR description for a consensus refactor that improves throughput by 40%.
```
✓ Should generate: Markdown, professional tone, data-driven, linked issues

### Test 5: Channel Formatting
```
Get the Discord channel profile and explain how it shapes communication
```
✓ Should describe: threads, emoji, real-time chat, casual-professional tone

### Test 6: Vibe Application
```
Get the prestige vibe profile and show me how it affects language choices
```
✓ Should describe: formal language, data-driven, authoritative, avoid jargon

---

## Real-World Examples

### Example 1: GitHub PR (Technical)

**Input:**
- Project: ez_chain
- Role: core_engineer
- Channel: github
- Task: "Write a PR for the consensus validation refactor"

**Claude Process:**
1. `get_context("ez_chain", "core_engineer")`
2. Load: Markdown format, prestige vibe, GitHub best practices
3. Generate: Professional, data-driven, linked issues, clear rationale

**Output:**
```markdown
# refactor: optimize consensus validation for 40% throughput improvement

## Problem
Current validation loop has cache misses causing 40% of CPU time...

## Solution
Refactored to use RwLock with memory optimization...

## Testing
Unit tests: 24/24 passing
Concurrent stress test: 100% success rate
Benchmark: 40% improvement

Fixes #456
```

### Example 2: Discord Announcement (Community)

**Input:**
- Project: ez_up
- Role: community_manager
- Channel: discord
- Task: "Announce creator rewards launch"

**Claude Process:**
1. `get_context("ez_up", "community_manager")`
2. Load: Threads, emoji, builder vibe, community warmth
3. Generate: Energetic, friendly, action-oriented

**Output:**
```
🚀 **EZ UP Creator Rewards Are Live!**

Drop your content. Get paid. Watch your audience grow.

[Get Started →] [Docs] [Support]

Questions? Post in thread 👇
```

### Example 3: X Post (Public)

**Input:**
- Project: ZENDEX
- Role: founder
- Channel: x
- Task: "Announce institutional trading features"

**Claude Process:**
1. `get_context("zendex", "founder")`
2. Load: 280 chars, prestige+public vibes, X best practices
3. Generate: Punchy, authoritative, institutional credibility

**Output:**
```
ZENDEX: Institutional-grade trading.
ZK privacy. Deterministic routing. Premium UX.
Live now for institutions and funds.

https://zendex.io
```

---

## Troubleshooting

### "MCP tools not available"
- Ensure MCP server is running (`python3 mcp/server.py`)
- Check MCP configuration in Claude settings
- Restart Claude to reload MCP config

### "Profile not found"
- Check spelling (case-sensitive): `ez_chain` not `EZ Chain`
- List available: `list_profiles(type="projects")`
- Verify file exists: `ls profiles/projects/`

### "Context incomplete"
- Ensure both project and role exist
- Check: `get_project("name")` and `get_role("name")` individually
- Then try: `get_context("project", "role")`

### "Output not shaped by profiles"
- Verify context was retrieved in the Claude response
- Check that vibe/channel profiles were included
- Review the do/dont lists from profiles
- Ensure Claude system prompt includes instructions to apply profiles

---

## Verification

**Phase 4b is complete when:**

- [ ] MCP server runs without errors
- [ ] All 6 tools are available in Claude
- [ ] `get_context` returns full orchestration context
- [ ] Claude can load and apply profiles
- [ ] Test outputs are shaped by vibe + channel
- [ ] Multiple projects/roles work correctly
- [ ] Documentation is complete

---

## Next: Phase 5

Once Phase 4b is verified, move to Phase 5:

**Phase 5: Orchestrator Logic**

Build the "if input → then apply profiles" layer:
- Context detection (auto-identify project/role/channel)
- Auto-selection of profiles
- Automatic output formatting
- Multi-channel routing

---

## Status

**Phase 4b Goal:** Claude becomes profile-aware ✓

**Next Step:** Test with real prompts, then move to Phase 5

**Timeline:** 2-4 hours to full integration + testing
